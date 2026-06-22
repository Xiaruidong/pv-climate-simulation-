"""
FastAPI后端服务
提供光伏气候效应模拟的API接口
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
import logging
from datetime import datetime
import uuid

from ebm_core import ebm_model

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="光伏气候效应模拟API",
    description="基于EBM模型的光伏建设气候效应评估服务",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 存储模拟任务状态
simulation_tasks = {}


# 定义数据模型
class SimulationParams(BaseModel):
    """模拟参数模型"""
    albedo_land: float = Field(default=0.3, description="陆地反照率", ge=0, le=1)
    albedo_ocean: float = Field(default=0.15, description="海洋反照率", ge=0, le=1)
    albedo_pv: float = Field(default=0.438, description="光伏面板反照率", ge=0, le=1)
    coverage_ratio: float = Field(default=0.01, description="光伏覆盖面积比例", ge=0, le=1)
    co2_current: float = Field(default=420, description="当前CO2浓度(ppm)", ge=0)
    initial_temp: float = Field(default=8.0, description="初始地表温度(℃)")
    simulation_years: int = Field(default=100, description="模拟年数", ge=1, le=1000)
    pv_efficiency: float = Field(default=0.23, description="光电转化效率", ge=0, le=1)


class TaskResponse(BaseModel):
    """任务响应模型"""
    task_id: str
    status: str
    message: str


class SimulationResult(BaseModel):
    """模拟结果模型"""
    success: bool
    data: Optional[Dict] = None
    error: Optional[str] = None


# 预设的光伏面板类型
PV_PANEL_TYPES = {
    "new": {
        "name": "新型透过+反射选择性光伏面板",
        "albedo_effective": 0.438,
        "albedo_panel": 0.27,
        "efficiency": 0.23,
        "description": "高反照率+高转化效率，双重降温效应"
    },
    "traditional": {
        "name": "传统光伏面板",
        "albedo_effective": 0.307,
        "albedo_panel": 0.1,
        "efficiency": 0.23,
        "description": "中等反照率+标准转化效率"
    },
    "mirror": {
        "name": "镜面反射型光伏面板",
        "albedo_effective": 0.95,
        "albedo_panel": 0.95,
        "efficiency": 0.23,
        "description": "超高反照率，降温效应最强"
    }
}


@app.get("/")
async def root():
    """API根路径"""
    return {
        "message": "光伏气候效应模拟API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/panel-types")
async def get_panel_types():
    """获取可用的光伏面板类型"""
    return {
        "panel_types": PV_PANEL_TYPES,
        "coverage_ratios": [0.0001, 0.001, 0.01, 0.1],
        "co2_scenarios": {
            "current": 420,
            "pre_industrial": 280,
            "paris_agreement": 450
        }
    }


@app.get("/api/parameters/default")
async def get_default_parameters():
    """获取默认参数"""
    return {
        "albedo_land": 0.3,
        "albedo_ocean": 0.15,
        "albedo_pv": 0.438,
        "coverage_ratio": 0.01,
        "co2_current": 420,
        "initial_temp": 8.0,
        "simulation_years": 100,
        "pv_efficiency": 0.23,
        "recommended_values": {
            "coverage_ratios": [0.0001, 0.001, 0.01, 0.1],
            "simulation_years": [50, 100, 200, 500]
        }
    }


@app.post("/api/parameters/validate")
async def validate_parameters(params: SimulationParams):
    """参数验证"""
    errors = []
    warnings = []

    # 参数范围检查
    if params.albedo_pv < 0 or params.albedo_pv > 1:
        errors.append("光伏面板反照率必须在0-1之间")

    if params.coverage_ratio < 0 or params.coverage_ratio > 1:
        errors.append("覆盖面积比例必须在0-1之间")

    if params.co2_current < 280 or params.co2_current > 1000:
        warnings.append("CO2浓度超出典型范围(280-1000ppm)")

    if params.simulation_years > 500:
        warnings.append("模拟时间超过500年，计算时间可能较长")

    # 物理合理性检查
    if params.coverage_ratio > 0.5:
        warnings.append("光伏覆盖面积超过50%，可能不现实")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "estimated_duration": f"{params.simulation_years * 0.01:.1f}秒"
    }


def run_simulation_task(task_id: str, params: SimulationParams):
    """后台运行模拟任务"""
    try:
        simulation_tasks[task_id]["status"] = "running"

        # 运行模拟
        result = ebm_model.run_simulation(params.dict())

        # 保存结果
        simulation_tasks[task_id]["status"] = "completed"
        simulation_tasks[task_id]["result"] = result
        simulation_tasks[task_id]["completed_at"] = datetime.now().isoformat()

        logger.info(f"任务 {task_id} 完成")

    except Exception as e:
        simulation_tasks[task_id]["status"] = "failed"
        simulation_tasks[task_id]["error"] = str(e)
        logger.error(f"任务 {task_id} 失败: {str(e)}")


@app.post("/api/simulate", response_model=TaskResponse)
async def start_simulation(params: SimulationParams, background_tasks: BackgroundTasks):
    """启动模拟计算"""
    # 生成任务ID
    task_id = str(uuid.uuid4())

    # 创建任务记录
    simulation_tasks[task_id] = {
        "task_id": task_id,
        "status": "pending",
        "params": params.dict(),
        "created_at": datetime.now().isoformat()
    }

    # 启动后台任务
    background_tasks.add_task(run_simulation_task, task_id, params)

    logger.info(f"启动模拟任务 {task_id}")

    return TaskResponse(
        task_id=task_id,
        status="pending",
        message="模拟任务已启动"
    )


@app.get("/api/simulate/{task_id}", response_model=SimulationResult)
async def get_simulation_result(task_id: str):
    """获取模拟结果"""
    if task_id not in simulation_tasks:
        raise HTTPException(status_code=404, detail="任务不存在")

    task = simulation_tasks[task_id]

    if task["status"] == "completed":
        return SimulationResult(
            success=True,
            data=task["result"]
        )
    elif task["status"] == "failed":
        return SimulationResult(
            success=False,
            error=task.get("error", "未知错误")
        )
    else:
        return SimulationResult(
            success=False,
            error=f"任务仍在运行中，当前状态: {task['status']}"
        )


@app.get("/api/simulate/{task_id}/status")
async def get_task_status(task_id: str):
    """获取任务状态"""
    if task_id not in simulation_tasks:
        raise HTTPException(status_code=404, detail="任务不存在")

    task = simulation_tasks[task_id]
    return {
        "task_id": task_id,
        "status": task["status"],
        "created_at": task["created_at"],
        "completed_at": task.get("completed_at"),
        "params": task["params"]
    }


@app.post("/api/simulate/batch")
async def run_batch_simulation(params_list: List[SimulationParams]):
    """批量模拟（不同面板类型和覆盖面积）"""
    task_ids = []

    for params in params_list:
        task_id = str(uuid.uuid4())
        task_ids.append(task_id)

        simulation_tasks[task_id] = {
            "task_id": task_id,
            "status": "pending",
            "params": params.dict(),
            "created_at": datetime.now().isoformat()
        }

    logger.info(f"启动批量模拟，包含 {len(params_list)} 个任务")

    return {
        "batch_id": str(uuid.uuid4()),
        "task_count": len(params_list),
        "task_ids": task_ids,
        "message": "批量模拟任务已启动"
    }


@app.get("/api/results/comparison")
async def get_comparison_results():
    """获取预设场景对比结果"""
    # 预设对比场景
    scenarios = [
        {
            "name": "新型面板 1%覆盖",
            "panel_type": "new",
            "coverage": 0.01,
            "description": "推荐方案，平衡降温效果和可行性"
        },
        {
            "name": "新型面板 10%覆盖",
            "panel_type": "new",
            "coverage": 0.1,
            "description": "激进方案，最大降温效果"
        },
        {
            "name": "传统面板 1%覆盖",
            "panel_type": "traditional",
            "coverage": 0.01,
            "description": "对比基准"
        },
        {
            "name": "镜面面板 1%覆盖",
            "panel_type": "mirror",
            "coverage": 0.01,
            "description": "纯反照率效应方案"
        }
    ]

    return {
        "scenarios": scenarios,
        "note": "这些是预设的典型场景，可以基于它们进行详细计算"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
