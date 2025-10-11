import abc
from typing import Dict, List, Optional, Tuple

# 第三方库
import mlflow
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
from tsfresh import extract_relevant_features, extract_features
from tsfresh.feature_extraction import EfficientFCParameters


class BaseAnomalyDetection(abc.ABC):
    """异常检测基类，提供通用的训练和预测功能"""

    @abc.abstractmethod
    def build_model(self, train_params: dict):
        """
        构建模型实例

        Args:
            train_params: 训练参数字典

        Returns:
            具备 fit(X, y) 方法的模型，最好同时支持 predict_proba 或 decision_function
        """
        pass

    def preprocess(self, df: pd.DataFrame, frequency: Optional[str] = None) -> Tuple[pd.DataFrame, List[str], Optional[str]]:
        """
        数据预处理：时间标准化、排序、缺失值填充

        Args:
            df: 输入数据框
            frequency: 时间频率，如果为None则自动推断

        Returns:
            处理后的数据框、特征列名列表、推断的频率
        """
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
        value_series = value_series.interpolate(
            method="time", limit_direction="both")
        value_series = value_series.ffill().bfill()

        if value_series.isna().any():
            median_value = value_series.median() if not np.isnan(
                value_series.median()) else 0.0
            value_series = value_series.fillna(median_value)
            logger.info(f"使用中位数 {median_value} 填充剩余缺失值")

        df["value"] = value_series

        # 恢复timestamp列
        df = df.reset_index()
        feature_columns = ["value"]

        return df, feature_columns, frequency

    def feature_engineer(
        self,
        df: pd.DataFrame,
        *,
        tsfresh_params: Optional[Dict] = None,
        n_jobs: int = 0,
        selected_features: Optional[List[str]] = None
    ) -> Tuple[pd.DataFrame, pd.Series, List[str]]:
        """特征工程：使用tsfresh提取时序特征"""
        if df is None:
            raise ValueError("feature_engineer 收到 None 的 df")

        logger.info(f"开始特征工程，输入数据形状: {df.shape}")
        df = df.copy()

        # 数据验证
        required_cols = ["label", "timestamp", "value"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"数据框缺少必需列: {missing_cols}")

        # 数据类型转换和清理
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        df["label"] = pd.to_numeric(df["label"], errors="coerce")

        initial_count = len(df)
        df = df.dropna(subset=required_cols).sort_values("timestamp")
        final_count = len(df)

        if initial_count != final_count:
            logger.warning(f"移除了 {initial_count - final_count} 行无效数据")

        if df.empty:
            raise ValueError("清理后数据为空，无法进行特征工程")

        if len(df) < 3:
            logger.warning(f"数据量较少 ({len(df)} 条)，特征提取可能受影响")

        # 准备时序数据
        df = df.reset_index(drop=True)
        df["_id"] = df.index
        y = df["label"].astype(int)
        y.index = df["_id"]

        timeseries_data = df[["_id", "timestamp", "value"]].copy()

        # 确保时间戳格式
        if not pd.api.types.is_datetime64_any_dtype(timeseries_data["timestamp"]):
            timeseries_data["timestamp"] = pd.to_datetime(
                timeseries_data["timestamp"])

        logger.info(f"准备提取特征，时序数据形状: {timeseries_data.shape}")
        logger.info(f"时间序列ID数量: {timeseries_data['_id'].nunique()}")

        # 配置tsfresh参数
        fc_params = EfficientFCParameters()
        if tsfresh_params and isinstance(tsfresh_params, dict):
            fc_params.update(tsfresh_params)
            logger.info(f"使用自定义tsfresh参数: {len(tsfresh_params)} 个配置")

        # 特征提取
        try:
            if selected_features is None:
                logger.info("开始提取相关特征，显示进度条...")
                X = extract_relevant_features(
                    timeseries_container=timeseries_data,
                    y=y,
                    column_id="_id",
                    column_sort="timestamp",
                    default_fc_parameters=fc_params,
                    n_jobs=0,  # 使用单线程避免问题
                    disable_progressbar=False,  # 启用进度条
                    show_warnings=False  # 减少警告信息
                )
            else:
                logger.info(f"开始提取指定的 {len(selected_features)} 个特征，显示进度条...")
                X_all = extract_features(
                    timeseries_container=timeseries_data,
                    column_id="_id",
                    column_sort="timestamp",
                    default_fc_parameters=fc_params,
                    n_jobs=0,
                    disable_progressbar=False,  # 启用进度条
                    show_warnings=False
                )
                available_features = [
                    f for f in selected_features if f in X_all.columns]
                X = X_all[available_features] if available_features else pd.DataFrame()
                logger.info(
                    f"从 {X_all.shape[1]} 个原始特征中选择了 {len(available_features)} 个目标特征")

            logger.info(f"✓ tsfresh特征提取完成，获得 {X.shape[1]} 个特征")

        except Exception as e:
            logger.error(f"✗ tsfresh特征提取失败: {e}")
            logger.info("⚠ 使用后备统计特征...")
            X = self._create_fallback_features(df)

        # 后处理
        if X.empty or X.shape[1] == 0:
            logger.warning("⚠ 无有效特征，使用后备特征")
            X = self._create_fallback_features(df)

        # 清理异常值
        X = X.replace([np.inf, -np.inf], np.nan).fillna(0)

        feature_cols = list(X.columns)
        logger.info(f"✓ 特征工程完成: {len(feature_cols)} 个特征, {len(X)} 个样本")

        return X.reset_index(drop=True), y.reset_index(drop=True), feature_cols

    def _create_fallback_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """创建基础统计特征作为后备"""
        return pd.DataFrame({
            'value_mean': [df['value'].mean()] * len(df),
            'value_std': [df['value'].std()] * len(df),
            'value_min': [df['value'].min()] * len(df),
            'value_max': [df['value'].max()] * len(df)
        })

    def predict(
        self,
        data: pd.DataFrame,
        model_name: str,
        model_version: str = "latest",
        threshold: float = 0.5
    ) -> pd.DataFrame:
        """
        使用训练好的模型进行异常检测预测

        Args:
            data: 包含timestamp和value列的DataFrame
            model_name: 模型名称
            model_version: 模型版本
            threshold: 异常检测阈值

        Returns:
            包含预测结果的DataFrame
        """
        # 加载模型及其元数据
        model_uri = f"models:/{model_name}/{model_version}"
        model = mlflow.sklearn.load_model(model_uri)

        feature_cols = getattr(model, "feature_cols", None)
        frequency = getattr(model, "frequency", None)
        tsfresh_params = getattr(model, "tsfresh_params", None)

        if feature_cols is None:
            raise ValueError("模型缺少feature_cols属性")

        # 数据预处理
        test_df, _, _ = self.preprocess(data, frequency)

        # 特征提取
        X_test = self._extract_prediction_features(
            test_df, feature_cols, tsfresh_params
        )

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

    def _extract_prediction_features(
        self,
        test_df: pd.DataFrame,
        feature_cols: List[str],
        tsfresh_params: Optional[Dict]
    ) -> pd.DataFrame:
        """提取预测所需的特征"""
        logger.info(f"提取预测特征，目标特征数: {len(feature_cols)}")

        test_df_for_feature = test_df.copy()
        test_df_for_feature = test_df_for_feature.reset_index(drop=True)
        test_df_for_feature["_id"] = test_df_for_feature.index

        # 配置参数
        fc_params = EfficientFCParameters()
        if tsfresh_params and isinstance(tsfresh_params, dict):
            fc_params.update(tsfresh_params)

        # 提取特征
        try:
            logger.info("提取预测特征中，显示进度条...")
            X_all = extract_features(
                timeseries_container=test_df_for_feature[
                    "_id", "timestamp", "value"],
                column_id="_id",
                column_sort="timestamp",
                default_fc_parameters=fc_params,
                n_jobs=0,
                disable_progressbar=False,  # 启用进度条
                show_warnings=False  # 减少警告信息
            )
            logger.info(f"✓ 成功提取 {X_all.shape[1]} 个原始特征")
        except Exception as e:
            logger.error(f"✗ 预测特征提取失败: {e}，使用后备特征")
            X_all = self._create_fallback_features(test_df_for_feature)

        # 选择和对齐特征
        available_features = [f for f in feature_cols if f in X_all.columns]
        missing_features = set(feature_cols) - set(available_features)

        if missing_features:
            logger.warning(f"⚠ 缺失 {len(missing_features)} 个特征，将用0填充")

        X_test = X_all[available_features].copy(
        ) if available_features else pd.DataFrame()
        for feat in missing_features:
            X_test[feat] = 0

        # 清理数据
        X_test = X_test.replace([np.inf, -np.inf], np.nan).fillna(0)

        logger.info(f"✓ 预测特征准备完成: {X_test.shape}")
        return X_test[feature_cols]

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
            return expit(decision_scores)  # 转换为概率形式
        else:
            return model.predict(X).astype(float)

    def _apply_threshold(self, scores: np.ndarray, threshold: float) -> np.ndarray:
        """根据阈值生成离散标签"""
        scores = np.asarray(scores)
        if np.issubdtype(scores.dtype, np.floating) and (np.unique(scores).size > 2):
            return (scores >= threshold).astype(int)
        else:
            return scores.astype(int)

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
        *,
        tsfresh_params: Optional[Dict] = None,
        n_jobs: int = 0,
        primary_metric: str = "f1",
        positive_label: int = 1,
        decision_threshold: float = 0.5
    ):
        """训练异常检测模型"""
        logger.info(f"开始训练模型: {model_name}")
        logger.info(
            f"训练数据: {train_dataframe.shape}, 验证数据: {val_dataframe.shape if val_dataframe is not None else 'None'}")

        # 设置MLflow
        self._setup_mlflow(mlflow_tracking_url, experiment_name)
        logger.info(f"MLflow实验: {experiment_name}")

        # 数据预处理
        logger.info("开始数据预处理...")
        preprocessing_result = self._preprocess_all_data(
            train_dataframe, val_dataframe, test_dataframe
        )
        train_df_prep, val_df_prep, test_df_prep, frequency = preprocessing_result
        logger.info(f"预处理完成，推断频率: {frequency}")

        # 特征工程
        logger.info("开始训练集特征工程...")
        X_train, y_train, feature_cols = self.feature_engineer(
            train_df_prep, tsfresh_params=tsfresh_params, n_jobs=n_jobs
        )

        # 准备验证集 - 如果没有提供验证集，从训练集分割
        if val_df_prep is None:
            logger.info("未提供验证集，从训练集分割20%作为验证集")
            from sklearn.model_selection import train_test_split
            X_train_split, X_val, y_train_split, y_val = train_test_split(
                X_train, y_train, test_size=0.2, random_state=42, stratify=y_train
            )
            X_train, y_train = X_train_split, y_train_split
            logger.info(f"分割后 - 训练集: {len(X_train)}, 验证集: {len(X_val)}")
        else:
            logger.info("开始验证集特征工程...")
            X_val, y_val, _ = self.feature_engineer(
                val_df_prep, tsfresh_params=tsfresh_params, n_jobs=n_jobs,
                selected_features=feature_cols
            )

        # 超参数优化
        logger.info(f"开始超参数优化，最大评估次数: {max_evals}")
        optimization_result = self._optimize_hyperparameters(
            train_config, X_train, y_train, X_val, y_val,
            max_evals, primary_metric, positive_label, decision_threshold
        )
        best_params, trials, train_scores_history, val_scores_history = optimization_result
        logger.info(f"超参数优化完成，最佳参数: {best_params}")

        # 使用全部训练数据训练最终模型
        logger.info("训练最终模型...")
        if val_df_prep is None:
            # 如果是从训练集分割的验证集，合并回去训练最终模型
            X_train_full = pd.concat([X_train, X_val], ignore_index=True)
            y_train_full = pd.concat([y_train, y_val], ignore_index=True)
        else:
            X_train_full, y_train_full = X_train, y_train

        best_model = self._train_final_model(
            best_params, X_train_full, y_train_full, feature_cols, frequency, tsfresh_params
        )

        # 评估模型
        val_metrics = self._evaluate_on_validation(best_model, X_val, y_val)
        test_metrics = self._evaluate_on_test(
            best_model, test_df_prep, feature_cols, tsfresh_params, n_jobs,
            decision_threshold, positive_label
        )

        logger.info(f"验证集指标: {val_metrics}")
        logger.info(f"测试集指标: {test_metrics}")

        # 记录到MLflow
        self._log_to_mlflow(
            best_params, max_evals, primary_metric, decision_threshold,
            len(feature_cols), len(X_train_full), X_val, test_metrics,
            train_scores_history, val_scores_history, val_metrics, test_metrics,
            best_model, model_name, feature_cols, frequency, tsfresh_params
        )

        logger.info(f"模型 {model_name} 训练完成")

        return {
            "best_params": best_params,
            "best_model": best_model,
            "train_features": {
                "X": X_train_full, "y": y_train_full, "feature_cols": feature_cols, "frequency": frequency,
            },
            "val_preprocessed": val_df_prep,
            "test_preprocessed": test_df_prep,
            "val_metrics": val_metrics,
            "test_metrics": test_metrics,
            "trials": trials
        }

    def _setup_mlflow(self, tracking_url: Optional[str], experiment_name: str):
        """设置MLflow配置"""
        if tracking_url:
            mlflow.set_tracking_uri(tracking_url)
        else:
            mlflow.set_tracking_uri("file:./mlruns")
        mlflow.set_experiment(experiment_name)

    def _preprocess_all_data(
        self,
        train_df: pd.DataFrame,
        val_df: Optional[pd.DataFrame],
        test_df: Optional[pd.DataFrame]
    ) -> Tuple[pd.DataFrame, Optional[pd.DataFrame], Optional[pd.DataFrame], Optional[str]]:
        """预处理所有数据集"""
        train_df_prep, _, frequency = self.preprocess(train_df, None)
        val_df_prep = self.preprocess(val_df, frequency)[
            0] if val_df is not None else None
        test_df_prep = self.preprocess(test_df, frequency)[
            0] if test_df is not None else None

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

        def objective(params_raw):
            params = space_eval(space, params_raw)

            try:
                model = self.build_model(train_params=params)
                model.fit(X_train, y_train)

                # 评估性能
                train_score = self._evaluate_model_score(
                    model, X_train, y_train, primary_metric, positive_label, decision_threshold
                )
                val_score = self._evaluate_model_score(
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

        return best_model

    def _evaluate_on_validation(
        self,
        model,
        X_val: Optional[pd.DataFrame],
        y_val: Optional[pd.Series]
    ) -> dict:
        """在验证集上评估模型"""
        val_metrics = {}
        if X_val is not None:
            val_scores = self._get_prediction_scores(model, X_val)
            try:
                val_metrics["auc"] = float(roc_auc_score(y_val, val_scores))
            except Exception as e:
                logger.warning(f"计算验证集AUC失败: {e}")
        return val_metrics

    def _evaluate_on_test(
        self,
        model,
        test_df_prep: Optional[pd.DataFrame],
        feature_cols: List[str],
        tsfresh_params: Optional[Dict],
        n_jobs: int,
        decision_threshold: float,
        positive_label: int
    ) -> dict:
        """在测试集上评估模型"""
        test_metrics = {}

        if (test_df_prep is not None and
            "label" in test_df_prep.columns and
                test_df_prep["label"].notna().any()):

            X_test, y_test, _ = self.feature_engineer(
                test_df_prep, tsfresh_params=tsfresh_params, n_jobs=n_jobs,
                selected_features=feature_cols
            )

            test_scores = self._get_prediction_scores(model, X_test)

            try:
                test_metrics["auc"] = float(roc_auc_score(y_test, test_scores))
            except Exception as e:
                logger.warning(f"计算测试集AUC失败: {e}")

            # 计算其他指标
            y_test_pred = self._apply_threshold(
                test_scores, decision_threshold)

            P, R, F1, _ = precision_recall_fscore_support(
                y_test, y_test_pred, pos_label=positive_label,
                average="binary", zero_division=0
            )

            test_metrics.update({
                "precision": float(P),
                "recall": float(R),
                "f1": float(F1),
                "accuracy": float(accuracy_score(y_test, y_test_pred)),
                "threshold": float(decision_threshold),
            })

        return test_metrics

    def _log_to_mlflow(
        self,
        best_params: dict,
        max_evals: int,
        primary_metric: str,
        decision_threshold: float,
        n_features: int,
        n_train_samples: int,
        X_val: Optional[pd.DataFrame],
        test_metrics: dict,
        train_scores_history: List[float],
        val_scores_history: List[float],
        val_metrics: dict,
        test_metrics_final: dict,
        best_model,
        model_name: str,
        feature_cols: List[str],
        frequency: Optional[str],
        tsfresh_params: Optional[Dict]
    ):
        """记录训练结果到MLflow"""
        with mlflow.start_run():
            # 记录超参数
            mlflow.log_params(best_params)
            mlflow.log_param("max_evals", max_evals)
            mlflow.log_param("primary_metric", primary_metric)
            mlflow.log_param("decision_threshold", decision_threshold)
            mlflow.log_param("n_features", n_features)
            mlflow.log_param("train_samples", n_train_samples)

            if X_val is not None:
                mlflow.log_param("val_samples", len(X_val))
            if test_metrics:
                mlflow.log_param("test_samples", len(test_metrics))

            # 记录训练过程
            for i, (train_score, val_score) in enumerate(zip(train_scores_history, val_scores_history), 1):
                mlflow.log_metric(
                    f"train_{primary_metric}", train_score, step=i)
                mlflow.log_metric(f"val_{primary_metric}", val_score, step=i)
                mlflow.log_metric(
                    "overfitting", train_score - val_score, step=i)

            # 记录最终指标
            if val_metrics:
                mlflow.log_metrics(
                    {f"val_{k}": v for k, v in val_metrics.items()})
            if test_metrics_final:
                mlflow.log_metrics(
                    {f"test_{k}": v for k, v in test_metrics_final.items()})

            # 保存模型
            mlflow.sklearn.log_model(
                sk_model=best_model,
                registered_model_name=model_name
            )
