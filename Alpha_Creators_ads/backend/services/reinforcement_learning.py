"""
Reinforcement Learning Module for Ad Optimization
Deep Q-Network (DQN) implementation for dynamic ad optimization
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from collections import deque, namedtuple
import random
import json
import logging
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime, timedelta
import asyncio

from core.config import settings
from core.database import get_db_session
from models import ReinforcementLearningModel, AdCreative, Campaign, AdDelivery

logger = logging.getLogger(__name__)

# Experience replay memory
Experience = namedtuple('Experience', ['state', 'action', 'reward', 'next_state', 'done'])


class AdOptimizationDQN(nn.Module):
    """Deep Q-Network for ad optimization decisions"""
    
    def __init__(self, state_size: int = 20, action_size: int = 10, hidden_size: int = 128):
        super(AdOptimizationDQN, self).__init__()
        
        self.state_size = state_size
        self.action_size = action_size
        
        # Neural network layers
        self.fc1 = nn.Linear(state_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, hidden_size)
        self.fc4 = nn.Linear(hidden_size, action_size)
        
        # Dropout for regularization
        self.dropout = nn.Dropout(0.2)
        
    def forward(self, x):
        """Forward pass through the network"""
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = F.relu(self.fc2(x))
        x = self.dropout(x)
        x = F.relu(self.fc3(x))
        x = self.fc4(x)
        return x


class ReinforcementLearningEngine:
    """Main reinforcement learning engine for ad optimization"""
    
    def __init__(
        self,
        state_size: int = 20,
        action_size: int = 10,
        learning_rate: float = 0.001,
        gamma: float = 0.95,
        epsilon: float = 1.0,
        epsilon_min: float = 0.01,
        epsilon_decay: float = 0.995,
        memory_size: int = 10000,
        batch_size: int = 32
    ):
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.gamma = gamma  # Discount factor
        self.epsilon = epsilon  # Exploration rate
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.batch_size = batch_size
        
        # Initialize replay memory
        self.memory = deque(maxlen=memory_size)
        
        # Initialize DQN networks
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.q_network = AdOptimizationDQN(state_size, action_size).to(self.device)
        self.target_network = AdOptimizationDQN(state_size, action_size).to(self.device)
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=learning_rate)
        
        # Update target network
        self.update_target_network()
        
        # Training metrics
        self.training_step = 0
        self.total_reward = 0
        self.episode_rewards = []
        
    def update_target_network(self):
        """Copy weights from main network to target network"""
        self.target_network.load_state_dict(self.q_network.state_dict())
    
    def get_state_vector(self, campaign_data: Dict[str, Any]) -> np.ndarray:
        """Convert campaign and user data into state vector"""
        
        # Extract features for state representation
        features = []
        
        # Campaign performance features
        features.extend([
            campaign_data.get('impressions', 0) / 10000,  # Normalized impressions
            campaign_data.get('clicks', 0) / 1000,        # Normalized clicks
            campaign_data.get('conversions', 0) / 100,    # Normalized conversions
            campaign_data.get('ctr', 0),                  # Click-through rate
            campaign_data.get('conversion_rate', 0),      # Conversion rate
            campaign_data.get('spend', 0) / 1000,         # Normalized spend
        ])
        
        # Time-based features
        current_hour = datetime.now().hour / 24  # Normalized hour
        current_day = datetime.now().weekday() / 7  # Normalized day of week
        features.extend([current_hour, current_day])
        
        # Audience features
        audience = campaign_data.get('target_audience', {})
        features.extend([
            len(audience.get('interests', [])) / 10,  # Normalized interest count
            1.0 if 'technology' in str(audience) else 0.0,  # Tech interest
            1.0 if 'lifestyle' in str(audience) else 0.0,   # Lifestyle interest
            1.0 if 'business' in str(audience) else 0.0,    # Business interest
        ])
        
        # Platform features
        platform = campaign_data.get('platform', '').lower()
        features.extend([
            1.0 if platform == 'facebook' else 0.0,
            1.0 if platform == 'instagram' else 0.0,
            1.0 if platform == 'twitter' else 0.0,
            1.0 if platform == 'linkedin' else 0.0,
        ])
        
        # Sentiment features
        sentiment_data = campaign_data.get('sentiment_analysis', {})
        features.extend([
            sentiment_data.get('positive_ratio', 0.5),
            sentiment_data.get('negative_ratio', 0.3),
            sentiment_data.get('neutral_ratio', 0.2),
        ])
        
        # Pad or truncate to match state_size
        while len(features) < self.state_size:
            features.append(0.0)
        features = features[:self.state_size]
        
        return np.array(features, dtype=np.float32)
    
    def get_action(self, state: np.ndarray, training: bool = True) -> int:
        """Choose action using epsilon-greedy policy"""
        
        if training and random.random() < self.epsilon:
            # Exploration: random action
            return random.randint(0, self.action_size - 1)
        else:
            # Exploitation: best action from Q-network
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            with torch.no_grad():
                q_values = self.q_network(state_tensor)
                return q_values.argmax().item()
    
    def action_to_optimization(self, action: int) -> Dict[str, Any]:
        """Convert action index to optimization parameters"""
        
        # Define action space
        optimizations = {
            0: {"type": "budget_increase", "value": 1.1},
            1: {"type": "budget_decrease", "value": 0.9},
            2: {"type": "audience_expand", "value": "broader"},
            3: {"type": "audience_narrow", "value": "narrower"},
            4: {"type": "creative_refresh", "value": "new_variation"},
            5: {"type": "bid_increase", "value": 1.2},
            6: {"type": "bid_decrease", "value": 0.8},
            7: {"type": "schedule_optimize", "value": "peak_hours"},
            8: {"type": "platform_shift", "value": "better_performing"},
            9: {"type": "no_change", "value": "maintain"}
        }
        
        return optimizations.get(action, optimizations[9])
    
    def calculate_reward(
        self, 
        previous_metrics: Dict[str, float], 
        current_metrics: Dict[str, float],
        optimization_cost: float = 0.0
    ) -> float:
        """Calculate reward based on performance improvement"""
        
        # Performance improvement weights
        weights = {
            'ctr_improvement': 10.0,
            'conversion_improvement': 15.0,
            'roas_improvement': 20.0,  # Return on Ad Spend
            'cost_efficiency': 5.0
        }
        
        reward = 0.0
        
        # CTR improvement
        ctr_prev = previous_metrics.get('ctr', 0)
        ctr_curr = current_metrics.get('ctr', 0)
        if ctr_prev > 0:
            ctr_improvement = (ctr_curr - ctr_prev) / ctr_prev
            reward += weights['ctr_improvement'] * ctr_improvement
        
        # Conversion rate improvement
        conv_prev = previous_metrics.get('conversion_rate', 0)
        conv_curr = current_metrics.get('conversion_rate', 0)
        if conv_prev > 0:
            conv_improvement = (conv_curr - conv_prev) / conv_prev
            reward += weights['conversion_improvement'] * conv_improvement
        
        # ROAS improvement
        spend_prev = previous_metrics.get('spend', 1)
        spend_curr = current_metrics.get('spend', 1)
        conv_value_prev = previous_metrics.get('conversions', 0) * 50  # Assuming $50 per conversion
        conv_value_curr = current_metrics.get('conversions', 0) * 50
        
        roas_prev = conv_value_prev / spend_prev if spend_prev > 0 else 0
        roas_curr = conv_value_curr / spend_curr if spend_curr > 0 else 0
        
        if roas_prev > 0:
            roas_improvement = (roas_curr - roas_prev) / roas_prev
            reward += weights['roas_improvement'] * roas_improvement
        
        # Cost efficiency (penalize if costs increase without proportional improvement)
        cost_change = spend_curr - spend_prev
        reward -= weights['cost_efficiency'] * max(0, cost_change / 100)
        
        # Penalty for optimization cost
        reward -= optimization_cost
        
        # Normalize reward to reasonable range [-1, 1]
        reward = np.tanh(reward)
        
        return reward
    
    def remember(self, state, action, reward, next_state, done):
        """Store experience in replay memory"""
        self.memory.append(Experience(state, action, reward, next_state, done))
    
    def replay_training(self):
        """Train the network using experience replay"""
        
        if len(self.memory) < self.batch_size:
            return
        
        # Sample random batch from memory
        batch = random.sample(self.memory, self.batch_size)
        states = torch.FloatTensor([e.state for e in batch]).to(self.device)
        actions = torch.LongTensor([e.action for e in batch]).to(self.device)
        rewards = torch.FloatTensor([e.reward for e in batch]).to(self.device)
        next_states = torch.FloatTensor([e.next_state for e in batch]).to(self.device)
        dones = torch.BoolTensor([e.done for e in batch]).to(self.device)
        
        # Current Q values
        current_q_values = self.q_network(states).gather(1, actions.unsqueeze(1))
        
        # Next Q values from target network
        with torch.no_grad():
            next_q_values = self.target_network(next_states).max(1)[0]
            target_q_values = rewards + (self.gamma * next_q_values * ~dones)
        
        # Compute loss
        loss = F.mse_loss(current_q_values.squeeze(), target_q_values)
        
        # Optimize
        self.optimizer.zero_grad()
        loss.backward()
        # Gradient clipping for stability
        torch.nn.utils.clip_grad_norm_(self.q_network.parameters(), 1.0)
        self.optimizer.step()
        
        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        
        self.training_step += 1
        
        # Update target network periodically
        if self.training_step % 100 == 0:
            self.update_target_network()
        
        return loss.item()
    
    async def optimize_campaign(
        self, 
        campaign_id: str, 
        current_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Main optimization method for a campaign"""
        
        try:
            # Get current state
            state = self.get_state_vector(current_metrics)
            
            # Choose action
            action = self.get_action(state, training=True)
            
            # Convert action to optimization parameters
            optimization = self.action_to_optimization(action)
            
            # Log the decision
            logger.info(f"RL optimization for campaign {campaign_id}: {optimization}")
            
            return {
                "campaign_id": campaign_id,
                "action": action,
                "optimization": optimization,
                "state": state.tolist(),
                "epsilon": self.epsilon,
                "training_step": self.training_step
            }
            
        except Exception as e:
            logger.error(f"Error in campaign optimization: {e}")
            return {"error": str(e)}
    
    async def update_from_feedback(
        self,
        campaign_id: str,
        previous_state: np.ndarray,
        action: int,
        previous_metrics: Dict[str, float],
        current_metrics: Dict[str, float],
        done: bool = False
    ):
        """Update the model based on campaign performance feedback"""
        
        try:
            # Calculate reward
            reward = self.calculate_reward(previous_metrics, current_metrics)
            
            # Get new state
            new_state = self.get_state_vector(current_metrics)
            
            # Store experience
            self.remember(previous_state, action, reward, new_state, done)
            
            # Train the model
            loss = self.replay_training()
            
            # Update metrics
            self.total_reward += reward
            if done:
                self.episode_rewards.append(self.total_reward)
                self.total_reward = 0
            
            logger.info(f"RL feedback for campaign {campaign_id}: reward={reward:.4f}, loss={loss}")
            
            return {
                "reward": reward,
                "loss": loss,
                "epsilon": self.epsilon,
                "memory_size": len(self.memory)
            }
            
        except Exception as e:
            logger.error(f"Error updating RL model: {e}")
            return {"error": str(e)}
    
    def save_model(self, filepath: str):
        """Save the trained model"""
        torch.save({
            'q_network_state_dict': self.q_network.state_dict(),
            'target_network_state_dict': self.target_network.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'epsilon': self.epsilon,
            'training_step': self.training_step,
            'episode_rewards': self.episode_rewards
        }, filepath)
        
        logger.info(f"RL model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load a trained model"""
        try:
            checkpoint = torch.load(filepath, map_location=self.device)
            
            self.q_network.load_state_dict(checkpoint['q_network_state_dict'])
            self.target_network.load_state_dict(checkpoint['target_network_state_dict'])
            self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
            self.epsilon = checkpoint['epsilon']
            self.training_step = checkpoint['training_step']
            self.episode_rewards = checkpoint['episode_rewards']
            
            logger.info(f"RL model loaded from {filepath}")
            
        except Exception as e:
            logger.error(f"Error loading RL model: {e}")
    
    def get_training_stats(self) -> Dict[str, Any]:
        """Get training statistics"""
        return {
            "training_step": self.training_step,
            "epsilon": self.epsilon,
            "memory_size": len(self.memory),
            "average_reward": np.mean(self.episode_rewards[-100:]) if self.episode_rewards else 0,
            "total_episodes": len(self.episode_rewards),
            "device": str(self.device)
        }


class RLCampaignManager:
    """Manager for RL-optimized campaigns"""
    
    def __init__(self):
        self.rl_engine = ReinforcementLearningEngine()
        self.active_campaigns: Dict[str, Dict] = {}
        
    async def start_optimization(self, campaign_id: str):
        """Start RL optimization for a campaign"""
        
        async with get_db_session() as db:
            # Get campaign data
            campaign_result = await db.execute(
                "SELECT * FROM campaigns WHERE id = :id",
                {"id": campaign_id}
            )
            campaign = campaign_result.first()
            
            if not campaign:
                raise ValueError(f"Campaign {campaign_id} not found")
            
            # Initialize campaign tracking
            self.active_campaigns[campaign_id] = {
                "start_time": datetime.utcnow(),
                "optimization_count": 0,
                "total_reward": 0.0,
                "previous_metrics": {},
                "current_state": None
            }
            
            logger.info(f"Started RL optimization for campaign {campaign_id}")
    
    async def run_optimization_cycle(self, campaign_id: str):
        """Run one optimization cycle for a campaign"""
        
        if campaign_id not in self.active_campaigns:
            await self.start_optimization(campaign_id)
        
        async with get_db_session() as db:
            # Get current campaign metrics
            metrics_result = await db.execute("""
                SELECT 
                    impressions, clicks, conversions, spend, ctr, conversion_rate,
                    target_audience, platform
                FROM campaigns 
                WHERE id = :id
            """, {"id": campaign_id})
            
            metrics = metrics_result.first()
            if not metrics:
                return {"error": "Campaign not found"}
            
            current_metrics = {
                "impressions": metrics.impressions,
                "clicks": metrics.clicks,
                "conversions": metrics.conversions,
                "spend": float(metrics.spend),
                "ctr": float(metrics.ctr),
                "conversion_rate": float(metrics.conversion_rate),
                "target_audience": metrics.target_audience,
                "platform": metrics.platform
            }
            
            # Run optimization
            optimization_result = await self.rl_engine.optimize_campaign(
                campaign_id, current_metrics
            )
            
            # Update campaign tracking
            campaign_tracking = self.active_campaigns[campaign_id]
            campaign_tracking["optimization_count"] += 1
            campaign_tracking["current_state"] = optimization_result.get("state")
            
            return optimization_result
    
    async def process_feedback(
        self, 
        campaign_id: str, 
        performance_data: Dict[str, float]
    ):
        """Process performance feedback and update RL model"""
        
        if campaign_id not in self.active_campaigns:
            return {"error": "Campaign not being optimized"}
        
        campaign_tracking = self.active_campaigns[campaign_id]
        previous_metrics = campaign_tracking.get("previous_metrics", {})
        previous_state = campaign_tracking.get("current_state")
        
        if previous_state is not None and previous_metrics:
            # Update RL model with feedback
            feedback_result = await self.rl_engine.update_from_feedback(
                campaign_id=campaign_id,
                previous_state=np.array(previous_state),
                action=0,  # Would need to track the actual action taken
                previous_metrics=previous_metrics,
                current_metrics=performance_data
            )
            
            # Update tracking
            campaign_tracking["previous_metrics"] = performance_data
            campaign_tracking["total_reward"] += feedback_result.get("reward", 0)
            
            return feedback_result
        
        return {"message": "No previous state for comparison"}


# Global RL manager instance
rl_manager = RLCampaignManager()
