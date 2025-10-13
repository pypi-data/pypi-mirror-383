import abc
from typing import Dict, List, Optional, Tuple

import mlflow
from neco.mlops.anomaly_detection.feature_engineer import TimeSeriesFeatureEngineer
import numpy as np
import pandas as pd
from loguru import logger
from hyperopt import fmin, tpe, Trials, STATUS_OK, hp, space_eval
from scipy.special import expit
from sklearn.metrics import (
    precision_recall_fscore_support,
    roc_auc_score,
    accuracy_score
)

from neco.mlops.utils.mlflow_utils import MLFlowUtils


class BaseAnomalyDetection(abc.ABC):
    """异常检测基类，提供通用的训练和预测功能"""

    def __init__(self):
        self.feature_engineer = None
        self.model_metadata = {}

    @abc.abstractmethod
    def build_model(self, train_params: dict):
        """构建模型实例"""
        pass

    def preprocess(self, df: pd.DataFrame, frequency: Optional[str] = None) -> Tuple[pd.DataFrame, List[str], Optional[str]]:
        """数据预处理：时间标准化、排序、缺失值填充"""
        if df is None:
            return None, [], frequency

        df = df.copy()

        # 标准化时间列并排序
        if not np.issubdtype(df["timestamp"].dtype, np.datetime64):
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df = df.dropna(subset=["timestamp"]).sort_values("timestamp")

        # 设置时间索引，推断频率
        df = df.set_index("timestamp")
        if frequency is None:
            try:
                frequency = pd.infer_freq(df.index)
            except Exception as e:
                logger.warning(f"无法推断时间频率: {e}")
                frequency = None

        # 处理缺失值：时间插值 -> 前后填充 -> 中位数兜底
        value_series = df["value"].astype(float)
        value_series = value_series.interpolate(method="time", limit_direction="both")
        value_series = value_series.ffill().bfill()

        if value_series.isna().any():
            median_value = value_series.median() if not np.isnan(value_series.median()) else 0.0
            value_series = value_series.fillna(median_value)

        df["value"] = value_series
        df = df.reset_index()

        return df, ["value"], frequency

    def predict(
        self,
        data: pd.DataFrame,
        model_name: str,
        model_version: str = "latest",
        threshold: float = 0.5
    ) -> pd.DataFrame:
        """使用训练好的模型进行异常检测预测"""
        # 加载模型及元数据
        model = self._load_model(model_name, model_version)
        
        # 打印加载的特征信息
        feature_cols = self.model_metadata.get("feature_cols")
        logger.info(f"📋 使用 {len(feature_cols)} 个特征进行预测")
        logger.debug(f"特征列表: {feature_cols[:10]}{'...' if len(feature_cols) > 10 else ''}")
        
        # 数据预处理
        test_df, _, _ = self.preprocess(data, self.model_metadata.get("frequency"))

        # 特征提取：直接使用保存的 feature_cols,无需 tsfresh_params
        feature_engineer = TimeSeriesFeatureEngineer(
            tsfresh_params=None,  # 不需要,因为我们使用 selected_features
            n_jobs=4
        )
        X_test, _, _ = feature_engineer.extract_features(
            test_df,
            selected_features=feature_cols,
            extract_labels=False
        )
        
        logger.info(f"✅ 测试数据特征提取完成，形状: {X_test.shape}")

        # 进行预测
        anomaly_scores = self._get_prediction_scores(model, X_test)
        anomaly_labels = self._apply_threshold(anomaly_scores, threshold)

        # 构建结果
        result_df = pd.DataFrame({
            'timestamp': test_df['timestamp'],
            'value': test_df['value'],
            'anomaly_probability': anomaly_scores,
            'anomaly_label': anomaly_labels
        })

        return result_df

    def train(
        self,
        model_name: str,
        train_dataframe: pd.DataFrame,
        val_dataframe: Optional[pd.DataFrame] = None,
        test_dataframe: Optional[pd.DataFrame] = None,
        train_config: dict = {},
        max_evals: int = 50,
        mlflow_tracking_url: Optional[str] = None,
        experiment_name: str = "Default",
        tsfresh_params: Optional[Dict] = None,
        n_jobs: int = 4,
        primary_metric: str = "f1",
        positive_label: int = 1,
        decision_threshold: float = 0.5
    ):
        """训练异常检测模型
        
        Args:
            model_name: 模型注册名称
            train_dataframe: 训练数据
            val_dataframe: 验证数据（可选）
            test_dataframe: 测试数据（可选）
            train_config: 超参数搜索空间配置
            max_evals: 超参数优化最大评估次数
            mlflow_tracking_url: MLflow tracking 服务地址
            experiment_name: 实验名称
            tsfresh_params: tsfresh 特征提取配置（None 表示使用所有默认特征）
            n_jobs: 并行任务数
            primary_metric: 优化的主要指标（f1/auc/precision/recall/accuracy）
            positive_label: 正类标签
            decision_threshold: 决策阈值
        """
        MLFlowUtils.setup_experiment(mlflow_tracking_url, experiment_name)

        # 初始化特征工程器
        self.feature_engineer = TimeSeriesFeatureEngineer(
            tsfresh_params=tsfresh_params,
            n_jobs=n_jobs
        )

        # 数据预处理
        logger.info("📊 开始数据预处理...")
        train_df_prep, val_df_prep, test_df_prep, frequency = self._preprocess_all_data(
            train_dataframe, val_dataframe, test_dataframe
        )

        # 特征工程
        logger.info("🔧 开始特征工程...")
        X_train, y_train, feature_cols = self.feature_engineer.extract_features(train_df_prep)
        
        # 打印特征信息
        logger.info(f"✅ 特征提取完成，共找到 {len(feature_cols)} 个有效特征")
        logger.info(f"特征名称列表: {feature_cols[:10]}{'...' if len(feature_cols) > 10 else ''}")
        
        # 准备验证集
        X_val, y_val = self._prepare_validation_set(
            val_df_prep, X_train, y_train, feature_cols
        )

        # 超参数优化
        logger.info(f"🔍 开始超参数优化，最大评估次数: {max_evals}")
        best_params, trials, train_scores, val_scores = self._optimize_hyperparameters(
            train_config, X_train, y_train, X_val, y_val,
            max_evals, primary_metric, positive_label, decision_threshold
        )

        # 训练最终模型
        logger.info("🚀 训练最终模型...")
        X_train_full, y_train_full = self._merge_train_val(
            X_train, y_train, X_val, y_val, val_df_prep
        )
        
        best_model = self._train_final_model(
            best_params, X_train_full, y_train_full,
            feature_cols, frequency, tsfresh_params
        )

        # 评估模型
        val_metrics = self._evaluate_model(best_model, X_val, y_val, "验证集")
        test_metrics = self._evaluate_test_set(
            best_model, test_df_prep, feature_cols,
            decision_threshold, positive_label
        )

        # 记录到MLflow
        self._log_to_mlflow(
            best_params, max_evals, primary_metric, decision_threshold,
            len(feature_cols), len(X_train_full), train_scores, val_scores,
            val_metrics, test_metrics, best_model, model_name
        )

        logger.info(f"✅ 模型 {model_name} 训练完成")

        return {
            "best_params": best_params,
            "best_model": best_model,
            "feature_cols": feature_cols,
            "val_metrics": val_metrics,
            "test_metrics": test_metrics,
            "trials": trials
        }

    def _load_model(self, model_name: str, model_version: str):
        """加载模型及元数据
        
        注意：
        - feature_cols 是必需的,用于特征提取
        - frequency 可以为 None(使用自动推断)
        - tsfresh_params 不需要加载(推理时只需要 feature_cols)
        """
        # 使用 MLFlowUtils 加载模型,只加载必要的元数据
        model, metadata = MLFlowUtils.load_model_with_metadata(
            model_name=model_name,
            model_version=model_version,
            metadata_attrs=["feature_cols", "frequency"]  # 移除 tsfresh_params
        )
        
        self.model_metadata = metadata
        
        # 只有 feature_cols 是必需的
        if self.model_metadata.get("feature_cols") is None:
            raise ValueError("模型缺少必需的元数据属性: feature_cols")
        
        # frequency 为 None 是合理的
        if self.model_metadata.get("frequency") is None:
            logger.debug("frequency 为 None,将在预测时自动推断")
        
        return model

    def _prepare_validation_set(
        self,
        val_df_prep: Optional[pd.DataFrame],
        X_train: pd.DataFrame,
        y_train: pd.Series,
        feature_cols: List[str]
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """准备验证集"""
        if val_df_prep is None:
            logger.info("未提供验证集，从训练集分割20%")
            from sklearn.model_selection import train_test_split
            X_train_split, X_val, y_train_split, y_val = train_test_split(
                X_train, y_train, test_size=0.2, random_state=42, stratify=y_train
            )
            return X_val, y_val
        else:
            logger.info("开始验证集特征工程...")
            X_val, y_val, _ = self.feature_engineer.extract_features(
                val_df_prep, selected_features=feature_cols
            )
            return X_val, y_val

    def _merge_train_val(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: pd.DataFrame,
        y_val: pd.Series,
        val_df_prep: Optional[pd.DataFrame]
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """合并训练集和验证集（如果验证集是从训练集分割的）"""
        if val_df_prep is None:
            X_train_full = pd.concat([X_train, X_val], ignore_index=True)
            y_train_full = pd.concat([y_train, y_val], ignore_index=True)
        else:
            X_train_full, y_train_full = X_train, y_train
        return X_train_full, y_train_full

    def _evaluate_model(
        self,
        model,
        X: Optional[pd.DataFrame],
        y: Optional[pd.Series],
        dataset_name: str
    ) -> dict:
        """评估模型性能"""
        metrics = {}
        if X is not None and y is not None:
            scores = self._get_prediction_scores(model, X)
            try:
                metrics["auc"] = float(roc_auc_score(y, scores))
                logger.info(f"{dataset_name} AUC: {metrics['auc']:.4f}")
            except Exception as e:
                logger.warning(f"计算{dataset_name}AUC失败: {e}")
        return metrics

    def _evaluate_test_set(
        self,
        model,
        test_df_prep: Optional[pd.DataFrame],
        feature_cols: List[str],
        threshold: float,
        positive_label: int
    ) -> dict:
        """评估测试集"""
        test_metrics = {}
        
        if (test_df_prep is not None and
            "label" in test_df_prep.columns and
            test_df_prep["label"].notna().any()):

            X_test, y_test, _ = self.feature_engineer.extract_features(
                test_df_prep, selected_features=feature_cols
            )

            test_scores = self._get_prediction_scores(model, X_test)

            try:
                test_metrics["auc"] = float(roc_auc_score(y_test, test_scores))
            except Exception as e:
                logger.warning(f"计算测试集AUC失败: {e}")

            y_test_pred = self._apply_threshold(test_scores, threshold)
            P, R, F1, _ = precision_recall_fscore_support(
                y_test, y_test_pred, pos_label=positive_label,
                average="binary", zero_division=0
            )

            test_metrics.update({
                "precision": float(P),
                "recall": float(R),
                "f1": float(F1),
                "accuracy": float(accuracy_score(y_test, y_test_pred)),
                "threshold": float(threshold),
            })
            
            logger.info(f"测试集指标: F1={F1:.4f}, AUC={test_metrics.get('auc', 0):.4f}")

        return test_metrics

    def _optimize_hyperparameters(
        self,
        train_config: dict,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: pd.DataFrame,
        y_val: pd.Series,
        max_evals: int,
        primary_metric: str,
        positive_label: int,
        decision_threshold: float
    ) -> Tuple[dict, Trials, List[float], List[float]]:
        """执行超参数优化"""
        space = self._build_search_space(train_config)
        if not space:
            logger.warning("未定义超参数搜索空间，使用默认参数")
            default_model = self.build_model({})
            return {}, Trials(), [], []

        logger.info(f"超参数搜索空间: {list(space.keys())}")

        trials = Trials()
        train_scores_history = []
        val_scores_history = []
        
        # 在闭包外部保存对基类实例的引用
        base_instance = self

        def objective(params_raw):
            params = space_eval(space, params_raw)

            try:
                # 使用 base_instance 而不是 self
                model = base_instance.build_model(train_params=params)
                model.fit(X_train, y_train)

                # 评估性能
                train_score = base_instance._evaluate_model_score(
                    model, X_train, y_train, primary_metric, positive_label, decision_threshold
                )
                val_score = base_instance._evaluate_model_score(
                    model, X_val, y_val, primary_metric, positive_label, decision_threshold
                )

                train_scores_history.append(train_score)
                val_scores_history.append(val_score)

                if len(train_scores_history) % 10 == 0:
                    logger.info(
                        f"第 {len(train_scores_history)} 次评估 - 训练{primary_metric}: {train_score:.4f}, 验证{primary_metric}: {val_score:.4f}")

                return {"loss": -float(val_score), "status": STATUS_OK}

            except Exception as e:
                logger.error(f"超参数评估失败: {e}")
                import traceback
                logger.debug(traceback.format_exc())
                return {"loss": 1.0, "status": STATUS_OK}

        logger.info("开始超参数搜索...")
        best_params_raw = fmin(
            fn=objective, space=space, algo=tpe.suggest, max_evals=max_evals,
            trials=trials, rstate=np.random.default_rng(2025)
        )
        best_params = space_eval(space, best_params_raw)

        if train_scores_history and val_scores_history:
            best_idx = np.argmax(val_scores_history)
            logger.info(
                f"最佳性能 - 训练{primary_metric}: {train_scores_history[best_idx]:.4f}, 验证{primary_metric}: {val_scores_history[best_idx]:.4f}")

        return best_params, trials, train_scores_history, val_scores_history

    def _evaluate_model_score(
        self,
        model,
        X: pd.DataFrame,
        y: pd.Series,
        metric: str,
        positive_label: int,
        threshold: float
    ) -> float:
        """评估模型在给定数据集上的性能"""
        scores = self._get_prediction_scores(model, X)
        return self._calculate_metric_score(y, scores, metric, threshold, positive_label)

    def _calculate_metric_score(
        self,
        y_true: pd.Series,
        scores: np.ndarray,
        metric: str,
        threshold: float,
        positive_label: int
    ) -> float:
        """计算指定指标的分数"""
        metric = metric.lower()
        scores = np.asarray(scores)
        is_continuous = (np.issubdtype(scores.dtype, np.floating) and
                         np.unique(scores).size > 2)

        if metric == "auc" and is_continuous:
            return roc_auc_score(y_true, scores)

        # 其他指标需要离散预测
        y_pred = ((scores >= threshold).astype(int) if is_continuous
                  else scores.astype(int))

        if metric == "auc":  # 离散情况下的AUC用准确率代替
            return accuracy_score(y_true, y_pred)

        P, R, F1, _ = precision_recall_fscore_support(
            y_true, y_pred, pos_label=positive_label, average="binary", zero_division=0
        )

        metric_map = {
            "f1": F1,
            "precision": P,
            "recall": R,
            "accuracy": accuracy_score(y_true, y_pred)
        }

        if metric not in metric_map:
            raise ValueError(f"不支持的指标: {metric}")

        return metric_map[metric]

    def _train_final_model(
        self,
        best_params: dict,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        feature_cols: List[str],
        frequency: Optional[str],
        tsfresh_params: Optional[Dict]
    ):
        """训练最终模型并保存元数据"""
        best_model = self.build_model(train_params=best_params)
        best_model.fit(X_train, y_train)

        # 保存元数据到模型对象
        best_model.feature_cols = feature_cols
        best_model.frequency = frequency
        best_model.tsfresh_params = tsfresh_params
        
        logger.info(f"💾 模型元数据已保存: {len(feature_cols)} 个特征, 频率={frequency}")

        return best_model

    def _preprocess_all_data(
        self,
        train_df: pd.DataFrame,
        val_df: Optional[pd.DataFrame],
        test_df: Optional[pd.DataFrame]
    ) -> Tuple[pd.DataFrame, Optional[pd.DataFrame], Optional[pd.DataFrame], Optional[str]]:
        """预处理所有数据集"""
        train_df_prep, _, frequency = self.preprocess(train_df, None)
        val_df_prep = self.preprocess(val_df, frequency)[0] if val_df is not None else None
        test_df_prep = self.preprocess(test_df, frequency)[0] if test_df is not None else None
        return train_df_prep, val_df_prep, test_df_prep, frequency

    def _build_search_space(self, train_config: dict) -> dict:
        """构建超参数搜索空间"""
        space = {}
        for key, cfg in train_config.items():
            param_type = str(cfg.get("type", "")).lower()

            if param_type == "randint":
                vmin, vmax = int(cfg["min"]), int(cfg["max"])
                if vmax < vmin:
                    raise ValueError(f"{key}: max({vmax}) < min({vmin})")
                space[key] = hp.randint(key, vmax - vmin + 1) + vmin

            elif param_type == "choice":
                opts = self._parse_choice_options(cfg["choice"])
                space[key] = hp.choice(key, opts)

        return space

    def _parse_choice_options(self, choices: List) -> List:
        """解析choice类型的选项"""
        opts = []
        for c in choices:
            if isinstance(c, str):
                lc = c.strip().lower()
                if lc == "none":
                    opts.append(None)
                elif lc == "true":
                    opts.append(True)
                elif lc == "false":
                    opts.append(False)
                else:
                    opts.append(c)
            else:
                opts.append(c)
        return opts

    def _log_to_mlflow(
        self,
        best_params: dict,
        max_evals: int,
        primary_metric: str,
        decision_threshold: float,
        n_features: int,
        n_train_samples: int,
        train_scores: List[float],
        val_scores: List[float],
        val_metrics: dict,
        test_metrics: dict,
        best_model,
        model_name: str
    ):
        """记录训练结果到MLflow"""
        # 合并所有参数
        all_params = {
            **best_params,
            "max_evals": max_evals,
            "primary_metric": primary_metric,
            "decision_threshold": decision_threshold,
            "n_features": n_features,
            "train_samples": n_train_samples
        }
        
        # 使用 MLFlowUtils 的一站式方法记录训练结果
        MLFlowUtils.log_training_results(
            params=all_params,
            train_scores=train_scores,
            val_scores=val_scores,
            metric_name=primary_metric,
            val_metrics=val_metrics,
            test_metrics=test_metrics,
            model=best_model,
            model_name=model_name
        )

    def _get_prediction_scores(self, model, X: pd.DataFrame) -> np.ndarray:
        """获取模型预测分数"""
        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(X)
            if isinstance(proba, np.ndarray) and proba.ndim == 2 and proba.shape[1] >= 2:
                return proba[:, 1]
            else:
                return model.predict(X).astype(float)
        elif hasattr(model, "decision_function"):
            decision_scores = model.decision_function(X)
            return expit(decision_scores)
        else:
            return model.predict(X).astype(float)

    def _apply_threshold(self, scores: np.ndarray, threshold: float) -> np.ndarray:
        """根据阈值生成离散标签"""
        scores = np.asarray(scores)
        if np.issubdtype(scores.dtype, np.floating) and (np.unique(scores).size > 2):
            return (scores >= threshold).astype(int)
        else:
            return scores.astype(int)
            return scores.astype(int)
