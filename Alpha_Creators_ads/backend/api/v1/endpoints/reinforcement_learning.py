"""
Reinforcement Learning optimization endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import uuid
import logging

from core.database import get_db_session
from models import User, Campaign, ReinforcementLearningModel
from services.authentication import get_current_user
from services.reinforcement_learning import rl_manager, ReinforcementLearningEngine

# Setup logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter()

# Pydantic models
from pydantic import BaseModel

class OptimizationRequest(BaseModel):
    campaign_id: str
    optimization_goal: str = "ctr"  # ctr, conversion_rate, roas
    learning_rate: Optional[float] = None
    auto_optimize: bool = True

class FeedbackData(BaseModel):
    campaign_id: str
    performance_metrics: Dict[str, float]
    time_period: str = "1h"  # 1h, 6h, 24h

class OptimizationResult(BaseModel):
    campaign_id: str
    action: int
    optimization: Dict[str, Any]
    confidence: float
    expected_improvement: Dict[str, float]
    timestamp: datetime

class TrainingStats(BaseModel):
    training_step: int
    epsilon: float
    memory_size: int
    average_reward: float
    total_episodes: int
    device: str

class ModelStatus(BaseModel):
    model_id: str
    status: str
    last_updated: datetime
    performance_metrics: Dict[str, float]
    active_campaigns: int


@router.post("/optimize", response_model=OptimizationResult)
async def optimize_campaign(
    request: OptimizationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Optimize a campaign using reinforcement learning"""
    
    if not current_user.is_advertiser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only advertisers can access optimization features"
        )
    
    # Verify campaign ownership
    campaign_result = await db.execute(
        "SELECT * FROM campaigns WHERE id = :id AND owner_id = :owner_id",
        {"id": request.campaign_id, "owner_id": current_user.id}
    )
    campaign = campaign_result.first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    try:
        # Run optimization
        optimization_result = await rl_manager.run_optimization_cycle(request.campaign_id)
        
        if "error" in optimization_result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Optimization failed: {optimization_result['error']}"
            )
        
        # Calculate expected improvement (simplified)
        expected_improvement = {
            "ctr_improvement": 0.15,  # 15% expected improvement
            "conversion_improvement": 0.12,  # 12% expected improvement
            "cost_reduction": 0.08   # 8% cost reduction
        }
        
        # Start auto-optimization if requested
        if request.auto_optimize:
            background_tasks.add_task(
                start_auto_optimization,
                request.campaign_id
            )
        
        return OptimizationResult(
            campaign_id=request.campaign_id,
            action=optimization_result.get("action", 0),
            optimization=optimization_result.get("optimization", {}),
            confidence=0.85,  # Would be calculated from model confidence
            expected_improvement=expected_improvement,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Optimization failed: {str(e)}"
        )


@router.post("/feedback")
async def submit_performance_feedback(
    feedback: FeedbackData,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Submit performance feedback to improve the RL model"""
    
    if not current_user.is_advertiser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only advertisers can submit feedback"
        )
    
    # Verify campaign ownership
    campaign_result = await db.execute(
        "SELECT id FROM campaigns WHERE id = :id AND owner_id = :owner_id",
        {"id": feedback.campaign_id, "owner_id": current_user.id}
    )
    if not campaign_result.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    try:
        # Process feedback
        feedback_result = await rl_manager.process_feedback(
            feedback.campaign_id,
            feedback.performance_metrics
        )
        
        if "error" in feedback_result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=feedback_result["error"]
            )
        
        # Store feedback in database for future analysis
        await db.execute("""
            INSERT INTO reinforcement_learning_feedback (
                id, campaign_id, user_id, performance_metrics, 
                reward, time_period, created_at
            ) VALUES (
                :id, :campaign_id, :user_id, :performance_metrics,
                :reward, :time_period, :created_at
            )
        """, {
            "id": str(uuid.uuid4()),
            "campaign_id": feedback.campaign_id,
            "user_id": current_user.id,
            "performance_metrics": str(feedback.performance_metrics),
            "reward": feedback_result.get("reward", 0.0),
            "time_period": feedback.time_period,
            "created_at": datetime.utcnow()
        })
        
        await db.commit()
        
        return {
            "message": "Feedback processed successfully",
            "reward": feedback_result.get("reward"),
            "model_updated": True,
            "training_step": feedback_result.get("training_step")
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process feedback: {str(e)}"
        )


@router.get("/status", response_model=TrainingStats)
async def get_training_status(
    current_user: User = Depends(get_current_user)
):
    """Get current training status of the RL model"""
    
    if not current_user.is_advertiser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only advertisers can view training status"
        )
    
    try:
        stats = rl_manager.rl_engine.get_training_stats()
        
        return TrainingStats(
            training_step=stats["training_step"],
            epsilon=stats["epsilon"],
            memory_size=stats["memory_size"],
            average_reward=stats["average_reward"],
            total_episodes=stats["total_episodes"],
            device=stats["device"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get training status: {str(e)}"
        )


@router.get("/models", response_model=List[ModelStatus])
async def get_model_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get status of all RL models"""
    
    if not current_user.is_advertiser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only advertisers can view model status"
        )
    
    try:
        # Get model information from database
        models_result = await db.execute("""
            SELECT 
                id, model_name, status, last_updated, performance_metrics,
                (SELECT COUNT(*) FROM campaigns WHERE rl_optimization = true AND owner_id = :user_id) as active_campaigns
            FROM reinforcement_learning_models 
            WHERE user_id = :user_id OR is_global = true
        """, {"user_id": current_user.id})
        
        models = models_result.all()
        
        model_statuses = []
        for model in models:
            model_statuses.append(ModelStatus(
                model_id=model.id,
                status=model.status,
                last_updated=model.last_updated,
                performance_metrics=model.performance_metrics or {},
                active_campaigns=model.active_campaigns or 0
            ))
        
        return model_statuses
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get model status: {str(e)}"
        )


@router.post("/campaigns/{campaign_id}/start")
async def start_campaign_optimization(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Start RL optimization for a specific campaign"""
    
    if not current_user.is_advertiser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only advertisers can start optimization"
        )
    
    # Verify campaign ownership
    campaign_result = await db.execute(
        "SELECT id FROM campaigns WHERE id = :id AND owner_id = :owner_id",
        {"id": campaign_id, "owner_id": current_user.id}
    )
    if not campaign_result.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    try:
        # Start optimization
        await rl_manager.start_optimization(campaign_id)
        
        # Update campaign to enable RL optimization
        await db.execute(
            "UPDATE campaigns SET rl_optimization = true WHERE id = :id",
            {"id": campaign_id}
        )
        await db.commit()
        
        return {
            "message": f"RL optimization started for campaign {campaign_id}",
            "campaign_id": campaign_id,
            "status": "active"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start optimization: {str(e)}"
        )


@router.post("/campaigns/{campaign_id}/stop")
async def stop_campaign_optimization(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Stop RL optimization for a specific campaign"""
    
    if not current_user.is_advertiser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only advertisers can stop optimization"
        )
    
    # Verify campaign ownership
    campaign_result = await db.execute(
        "SELECT id FROM campaigns WHERE id = :id AND owner_id = :owner_id",
        {"id": campaign_id, "owner_id": current_user.id}
    )
    if not campaign_result.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    try:
        # Remove from active campaigns
        if campaign_id in rl_manager.active_campaigns:
            del rl_manager.active_campaigns[campaign_id]
        
        # Update campaign to disable RL optimization
        await db.execute(
            "UPDATE campaigns SET rl_optimization = false WHERE id = :id",
            {"id": campaign_id}
        )
        await db.commit()
        
        return {
            "message": f"RL optimization stopped for campaign {campaign_id}",
            "campaign_id": campaign_id,
            "status": "stopped"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop optimization: {str(e)}"
        )


@router.get("/campaigns/{campaign_id}/performance")
async def get_optimization_performance(
    campaign_id: str,
    days: int = 7,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get optimization performance history for a campaign"""
    
    if not current_user.is_advertiser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only advertisers can view performance data"
        )
    
    # Verify campaign ownership
    campaign_result = await db.execute(
        "SELECT id FROM campaigns WHERE id = :id AND owner_id = :owner_id",
        {"id": campaign_id, "owner_id": current_user.id}
    )
    if not campaign_result.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get optimization history
        history_result = await db.execute("""
            SELECT 
                created_at, performance_metrics, reward
            FROM reinforcement_learning_feedback 
            WHERE campaign_id = :campaign_id 
            AND created_at >= :start_date
            ORDER BY created_at
        """, {"campaign_id": campaign_id, "start_date": start_date})
        
        history = history_result.all()
        
        # Calculate performance metrics
        performance_data = []
        total_reward = 0.0
        
        for record in history:
            metrics = eval(record.performance_metrics) if record.performance_metrics else {}
            reward = record.reward or 0.0
            total_reward += reward
            
            performance_data.append({
                "timestamp": record.created_at.isoformat(),
                "metrics": metrics,
                "reward": reward,
                "cumulative_reward": total_reward
            })
        
        # Get current campaign tracking info
        campaign_tracking = rl_manager.active_campaigns.get(campaign_id, {})
        
        return {
            "campaign_id": campaign_id,
            "optimization_active": campaign_id in rl_manager.active_campaigns,
            "total_optimizations": len(performance_data),
            "total_reward": total_reward,
            "average_reward": total_reward / len(performance_data) if performance_data else 0,
            "optimization_count": campaign_tracking.get("optimization_count", 0),
            "performance_history": performance_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get performance data: {str(e)}"
        )


@router.post("/train")
async def trigger_manual_training(
    epochs: int = 100,
    current_user: User = Depends(get_current_user)
):
    """Trigger manual training of the RL model"""
    
    if not current_user.is_advertiser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only advertisers can trigger training"
        )
    
    try:
        # Perform training epochs
        losses = []
        for _ in range(epochs):
            loss = rl_manager.rl_engine.replay_training()
            if loss is not None:
                losses.append(loss)
        
        avg_loss = sum(losses) / len(losses) if losses else 0
        
        return {
            "message": f"Manual training completed for {epochs} epochs",
            "epochs_trained": len(losses),
            "average_loss": avg_loss,
            "current_epsilon": rl_manager.rl_engine.epsilon,
            "training_step": rl_manager.rl_engine.training_step
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Training failed: {str(e)}"
        )


async def start_auto_optimization(campaign_id: str):
    """Background task to start auto-optimization for a campaign"""
    try:
        await rl_manager.start_optimization(campaign_id)
        logger.info(f"Auto-optimization started for campaign {campaign_id}")
    except Exception as e:
        logger.error(f"Failed to start auto-optimization for {campaign_id}: {e}")
