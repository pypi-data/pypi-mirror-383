import numpy as np
from sklearn.calibration import cross_val_predict
from sklearn.cross_decomposition import PLSRegression
from sklearn.metrics import mean_squared_error, r2_score, root_mean_squared_error
from sklearn.model_selection import train_test_split

def optimise_pls_cv(n_components,x, y, n_comp):
    try:
        mse = []
        if n_components == 0:
            component = np.arange(1, n_comp)
            for i in component:
                pls = PLSRegression(n_components=i)
                y_cv = cross_val_predict(pls, x, y, cv=8)
                mse.append(mean_squared_error(y, y_cv))
            MSE_MIN = np.argmin(mse)
            MSE_MIN += 1
            pass
        else:
            MSE_MIN = n_components
            pass
        pls_opt = PLSRegression(n_components=MSE_MIN)
        y, x = zip(*[(a, b) for a, b in zip(y, x) if a is not None])
        y=list(y)
        x=list(x)
        pls_opt.fit(x, y)
        return pls_opt, pls_opt.predict(x),MSE_MIN
    except Exception as e:
        raise ValueError(f"optimise_pls_cv:{str(e)}") from e
    
def optimise_pls_cv_jx(n_components, x, y, n_comp, test_size=0.3, random_state=42):
    try:
        # 1. 过滤无效样本
        filtered = [(a, b) for a, b in zip(y, x) if a is not None]
        if not filtered:
            raise ValueError("No valid samples after filtering (y contains None)")
        y_filtered, x_filtered = zip(*filtered)
        y_filtered = np.array(y_filtered)
        x_filtered = np.array(x_filtered)
        
        # 2. 拆分训练集和验证集
        x_train, x_val, y_train, y_val = train_test_split(
            x_filtered, y_filtered,
            test_size=test_size,
            random_state=random_state
        )
        
        # 3. 确定主成分数量并计算验证集指标（重点：直接计算RMSE）
        if n_components == 0:
            components = np.arange(1, n_comp)
            rmse_list = []  # 直接存储RMSE，不再用MSE列表
            r2_list = []
            for i in components:
                pls = PLSRegression(n_components=i)
                pls.fit(x_train, y_train)
                y_pred_val = pls.predict(x_val)
                y_pred_val_list = y_pred_val.tolist()
                
                # 直接计算RMSE（使用root_mean_squared_error）
                current_rmse = root_mean_squared_error(y_val, y_pred_val_list)
                current_r2 = r2_score(y_pred_val_list, y_val)
                rmse_list.append(current_rmse)
                r2_list.append(current_r2)
            
            # 选RMSE最小的主成分数（更直接）
            opt_idx = np.argmin(rmse_list)
            MSE_MIN = components[opt_idx]
            val_rmse = rmse_list[opt_idx]  # 直接取最小RMSE
            val_r2 = r2_list[opt_idx]
        
        else:
            MSE_MIN = n_components
            pls = PLSRegression(n_components=MSE_MIN)
            pls.fit(x_train, y_train)
            y_pred_val = pls.predict(x_val)
            y_pred_val_list = y_pred_val.tolist()
            
            # 直接计算RMSE
            val_rmse = root_mean_squared_error(y_val, y_pred_val_list)
            val_r2 = r2_score(y_pred_val_list, y_val)
        
        # 4. 全量数据训练最终模型
        pls_opt = PLSRegression(n_components=MSE_MIN)
        pls_opt.fit(x_filtered, y_filtered)
        y_pred_full = pls_opt.predict(x_filtered)
        
        # 返回：模型、全量预测、主成分数、验证集RMSE、验证集R²
        return pls_opt, y_pred_full, MSE_MIN, val_rmse, val_r2
    
    except Exception as e:
        raise ValueError(f"optimise_pls_cv: {str(e)}") from e