"""特征工程模块 - 负责时序数据的特征提取"""
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from loguru import logger
from tsfresh import extract_relevant_features, extract_features
from tsfresh.feature_extraction import EfficientFCParameters


class TimeSeriesFeatureEngineer:
    """时序特征工程器
    
    负责从时序数据中提取特征,支持训练和推理两种模式。
    """
    
    def __init__(
        self,
        tsfresh_params: Optional[Dict] = None,
        n_jobs: int = 4
    ):
        """初始化特征工程器
        
        Args:
            tsfresh_params: tsfresh特征提取参数
            n_jobs: 并行计算核心数
        """
        self.tsfresh_params = tsfresh_params or {}
        self.n_jobs = n_jobs
        
    def extract_features(
        self,
        df: pd.DataFrame,
        selected_features: Optional[List[str]] = None,
        extract_labels: bool = True
    ) -> Tuple[pd.DataFrame, Optional[pd.Series], List[str]]:
        """提取时序特征
        
        Args:
            df: 包含 timestamp, value, (label) 的数据框
            selected_features: 指定特征列表(推理模式)
            extract_labels: 是否提取标签
            
        Returns:
            (特征DataFrame, 标签Series, 特征名列表)
        """
        # 1. 数据验证与准备
        self._validate_data(df, extract_labels)
        df_prep = self._prepare_data(df)
        y = df_prep["label"].astype(int) if extract_labels else None
        
        # 2. 特征提取
        logger.info(f"开始特征提取 | 模式: {'训练' if selected_features is None else '推理'} | 样本数: {len(df_prep)}")
        fc_params = self._get_fc_parameters()
        
        X = (self._extract_relevant_features(df_prep, y, fc_params) 
             if selected_features is None 
             else self._extract_selected_features(df_prep, selected_features, fc_params))
        
        # 3. 后处理
        X = self._postprocess_features(X)
        
        logger.info(f"特征工程完成 | 特征数: {X.shape[1]} | 样本数: {X.shape[0]}")
        
        return X.reset_index(drop=True), (y.reset_index(drop=True) if y is not None else None), list(X.columns)
    
    def _validate_data(self, df: pd.DataFrame, extract_labels: bool):
        """验证输入数据完整性"""
        if df is None or df.empty:
            raise ValueError("输入数据为空")
        
        required_cols = ["timestamp", "value"] + (["label"] if extract_labels else [])
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            raise ValueError(f"缺少必需列: {', '.join(missing_cols)}")
    
    def _prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """准备时序数据"""
        df = df.copy()
        
        # 类型转换
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        if "label" in df.columns:
            df["label"] = pd.to_numeric(df["label"], errors="coerce")
        
        # 时间戳标准化
        if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
            df["timestamp"] = pd.to_datetime(df["timestamp"])
        
        # 清理并排序
        df = df.dropna(subset=["timestamp", "value"]).sort_values("timestamp").reset_index(drop=True)
        
        if df.empty:
            raise ValueError("数据清理后为空,请检查timestamp和value列")
        
        # 添加ID用于tsfresh
        df["_id"] = df.index
        
        return df
    
    def _get_fc_parameters(self) -> Dict:
        """获取特征计算参数"""
        params = EfficientFCParameters()
        params.update(self.tsfresh_params)
        return params
    
    def _extract_relevant_features(
        self,
        df: pd.DataFrame,
        y: pd.Series,
        fc_params: Dict
    ) -> pd.DataFrame:
        """提取相关特征(训练模式,基于标签过滤)"""
        timeseries_data = df[["_id", "timestamp", "value"]]
        y.index = df["_id"]
        
        try:
            X = extract_relevant_features(
                timeseries_container=timeseries_data,
                y=y,
                column_id="_id",
                column_sort="timestamp",
                default_fc_parameters=fc_params,
                n_jobs=self.n_jobs,
                disable_progressbar=False,
                show_warnings=False
            )
            logger.debug(f"提取到 {X.shape[1]} 个相关特征")
            return X
            
        except Exception as e:
            logger.warning(f"特征提取异常: {e}, 使用基础统计特征")
            return self._create_fallback_features(df)
    
    def _extract_selected_features(
        self,
        df: pd.DataFrame,
        selected_features: List[str],
        fc_params: Dict
    ) -> pd.DataFrame:
        """提取指定特征(推理模式)"""
        timeseries_data = df[["_id", "timestamp", "value"]]
        
        try:
            # 提取所有特征
            X_all = extract_features(
                timeseries_container=timeseries_data,
                column_id="_id",
                column_sort="timestamp",
                default_fc_parameters=fc_params,
                n_jobs=self.n_jobs,
                disable_progressbar=False,
                show_warnings=False
            )
            
            # 匹配目标特征
            available = [f for f in selected_features if f in X_all.columns]
            missing = set(selected_features) - set(available)
            
            if missing:
                logger.warning(f"缺失 {len(missing)} 个特征, 将填充为0")
            
            # 构建结果
            X = X_all[available].copy() if available else pd.DataFrame(index=X_all.index)
            for feat in missing:
                X[feat] = 0
            
            logger.debug(f"匹配特征: {len(available)}/{len(selected_features)}")
            return X[selected_features]
            
        except Exception as e:
            logger.warning(f"特征提取异常: {e}, 使用基础统计特征")
            return self._create_fallback_features(df)
    
    def _postprocess_features(self, X: pd.DataFrame) -> pd.DataFrame:
        """特征后处理: 清理异常值"""
        if X.empty or X.shape[1] == 0:
            logger.warning("特征为空, 返回零值DataFrame")
            return pd.DataFrame({'_fallback': [0]})
        
        # 替换无穷值和NaN
        X = X.replace([np.inf, -np.inf], np.nan).fillna(0)
        return X
    
    def _create_fallback_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """创建基础统计特征(后备方案)"""
        values = df['value']
        n_samples = len(df)
        
        return pd.DataFrame({
            'value_mean': [values.mean()] * n_samples,
            'value_std': [values.std()] * n_samples,
            'value_min': [values.min()] * n_samples,
            'value_max': [values.max()] * n_samples
        })
