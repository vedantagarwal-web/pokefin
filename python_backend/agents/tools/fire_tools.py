"""
FIRE Advisor Tools - Production Grade Implementation
Brutal portfolio roasting, FIRE calculations, and negotiation system
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import random
from dotenv import load_dotenv

load_dotenv()

from .registry import register_tool
from services.snaptrade_client import SnapTradeClient
from services.robinhood_client import RobinhoodClient

# Initialize clients
snaptrade_client = SnapTradeClient()
robinhood_client = RobinhoodClient()

@register_tool("roast_portfolio")
async def roast_portfolio(
    portfolio_data: Dict[str, Any] = None,
    user_age: int = 30,
    user_income: int = 50000,
    user_savings: int = 10000
) -> Dict[str, Any]:
    """
    🔥 BRUTAL PORTFOLIO ROAST: Analyze user's portfolio with brutal honesty like Poke roasts emails.
    Identifies meme stocks, over-concentration, terrible performance, and calculates FIRE requirements.
    """
    try:
        # Mock portfolio data for now (will connect to real brokerage later)
        if not portfolio_data:
            portfolio_data = {
                "positions": [
                    {"ticker": "TSLA", "shares": 10, "avg_cost": 200, "current_price": 180},
                    {"ticker": "GME", "shares": 50, "avg_cost": 40, "current_price": 25},
                    {"ticker": "DOGE", "shares": 10000, "avg_cost": 0.08, "current_price": 0.12}
                ],
                "total_value": 15000,
                "cash": 5000
            }
        
        # Calculate portfolio metrics
        total_invested = sum(pos["shares"] * pos["avg_cost"] for pos in portfolio_data["positions"])
        total_current = sum(pos["shares"] * pos["current_price"] for pos in portfolio_data["positions"])
        total_pnl = total_current - total_invested
        pnl_percent = (total_pnl / total_invested * 100) if total_invested else 0
        
        # Analyze holdings
        meme_stocks = ["GME", "AMC", "BB", "NOK", "DOGE", "SHIB", "APE", "BBBY", "EXPR", "NAKD"]
        tech_stocks = ["AAPL", "MSFT", "GOOGL", "NVDA", "TSLA", "META", "AMZN", "NFLX", "CRM", "ADBE"]
        
        tech_concentration = 0
        meme_allocation = 0
        individual_stocks = 0
        etf_allocation = 0
        
        for pos in portfolio_data["positions"]:
            ticker = pos["ticker"]
            position_value = pos["shares"] * pos["current_price"]
            allocation = position_value / total_current if total_current else 0
            
            if ticker in tech_stocks:
                tech_concentration += allocation
            if ticker in meme_stocks:
                meme_allocation += allocation
            if any(etf in ticker.upper() for etf in ["VTI", "VOO", "SPY", "QQQ", "VXUS", "BND"]):
                etf_allocation += allocation
            else:
                individual_stocks += allocation
        
        # Generate roast based on portfolio analysis
        roast_level = "MILD"
        roast_messages = []
        fire_reality = ""
        
        # Portfolio performance roast
        if pnl_percent < -30:
            roast_level = "BRUTAL"
            roast_messages.append(f"💀 Down {abs(pnl_percent):.0f}%. You're not investing, you're donating to the market.")
        elif pnl_percent < -10:
            roast_level = "HARSH"
            roast_messages.append(f"📉 Down {abs(pnl_percent):.0f}%. Your portfolio is bleeding money faster than a hemophiliac.")
        elif pnl_percent > 50:
            roast_level = "ENCOURAGING"
            roast_messages.append(f"🚀 Up {pnl_percent:.0f}%. Actually decent performance. I'm impressed.")
        
        # Meme stock roast
        if meme_allocation > 0.5:
            roast_level = "BRUTAL"
            roast_messages.append(f"🔥 Your portfolio is {meme_allocation:.0%} meme stocks. At this rate, you'll retire to your parents' basement, not the Bahamas.")
        elif meme_allocation > 0.2:
            roast_level = "HARSH"
            roast_messages.append(f"⚠️ {meme_allocation:.0%} in meme stocks. You're gambling, not investing.")
        
        # Tech concentration roast
        if tech_concentration > 0.8:
            roast_level = "HARSH" if roast_level != "BRUTAL" else "BRUTAL"
            roast_messages.append(f"📱 {tech_concentration:.0%} in tech stocks. Remember 2000? Your portfolio doesn't.")
        elif tech_concentration > 0.6:
            roast_messages.append(f"⚠️ {tech_concentration:.0%} in tech. Diversify before the next crash.")
        
        # Individual stock vs ETF roast
        if individual_stocks > 0.8:
            roast_messages.append(f"🎯 {individual_stocks:.0%} in individual stocks. You're playing stock picker instead of building wealth.")
        
        # Savings rate roast
        savings_rate = user_savings / user_income if user_income > 0 else 0
        if savings_rate < 0.1:
            roast_level = "BRUTAL" if roast_level != "BRUTAL" else "HARSH"
            roast_messages.append(f"📉 You save less than 10% of your income ({savings_rate:.0%}). FIRE at 40? More like FIRE at 65... if you're lucky.")
        elif savings_rate < 0.2:
            roast_messages.append(f"⚠️ Only {savings_rate:.0%} savings rate. You need to save more to achieve FIRE.")
        
        # Age-based roast
        if user_age > 40 and user_savings < 50000:
            roast_level = "BRUTAL" if roast_level != "BRUTAL" else "HARSH"
            roast_messages.append(f"⏰ You're {user_age} with less than $50K saved. Time to get serious about retirement.")
        
        # Default encouraging message if no major issues
        if not roast_messages:
            roast_messages.append("✅ Actually decent allocation. I'm impressed. You might actually retire before 70.")
            roast_level = "ENCOURAGING"
        
        # FIRE calculation
        monthly_income = user_income / 12
        monthly_savings = user_savings / 12 if user_savings > 0 else monthly_income * 0.1
        savings_rate = monthly_savings / monthly_income
        
        # Calculate FIRE requirements (25x annual expenses)
        annual_expenses = monthly_income * (1 - savings_rate) * 12
        fire_number = annual_expenses * 25
        
        # Calculate years to FIRE with compound growth
        current_net_worth = total_current + portfolio_data.get("cash", 0)
        annual_return = 0.07
        monthly_return = annual_return / 12
        
        months_to_fire = 0
        future_value = current_net_worth
        
        while future_value < fire_number and months_to_fire < 600:  # Max 50 years
            future_value = future_value * (1 + monthly_return) + monthly_savings
            months_to_fire += 1
        
        years_to_fire = months_to_fire / 12
        fire_age = user_age + years_to_fire
        
        # Generate FIRE reality check
        if fire_age > 70:
            fire_reality = f"💀 REALITY CHECK: You need ${fire_number:,.0f} to retire. At current savings rate, you'll FIRE at {fire_age:.0f}. Start saving more or work longer."
        elif fire_age > 60:
            fire_reality = f"⚠️ You're on track for FIRE at {fire_age:.0f}. Not terrible, but you could do better by increasing savings rate."
        elif fire_age > 50:
            fire_reality = f"📈 You're on track for FIRE at {fire_age:.0f}. Keep it up!"
        else:
            fire_reality = f"🚀 You're crushing it! On track for FIRE at {fire_age:.0f}. Keep it up!"
        
        # Generate recommendations
        recommendations = []
        
        if savings_rate < 0.25:
            recommendations.append("Increase savings rate to 25% minimum for FIRE")
        if meme_allocation > 0.1:
            recommendations.append("Sell meme stocks immediately and buy index funds")
        if tech_concentration > 0.6:
            recommendations.append("Diversify away from tech stocks")
        if individual_stocks > 0.7:
            recommendations.append("Consider VTI/VXUS for broad market exposure")
        if pnl_percent < -10:
            recommendations.append("Focus on index funds instead of stock picking")
        
        if not recommendations:
            recommendations.append("Keep doing what you're doing - you're on the right track!")
        
        return {
            "portfolio_summary": {
                "total_value": total_current,
                "total_invested": total_invested,
                "total_pnl": total_pnl,
                "pnl_percent": pnl_percent,
                "cash": portfolio_data.get("cash", 0)
            },
            "holdings_analysis": {
                "tech_concentration": tech_concentration,
                "meme_allocation": meme_allocation,
                "etf_allocation": etf_allocation,
                "individual_stocks": individual_stocks,
                "positions": portfolio_data["positions"]
            },
            "roast": {
                "level": roast_level,
                "messages": roast_messages
            },
            "fire_calculation": {
                "fire_number": fire_number,
                "current_net_worth": current_net_worth,
                "monthly_savings": monthly_savings,
                "savings_rate": savings_rate,
                "years_to_fire": years_to_fire,
                "fire_age": fire_age,
                "reality_check": fire_reality
            },
            "recommendations": recommendations
        }
        
    except Exception as e:
        print(f"❌ Error roasting portfolio: {e}")
        return {"error": str(e)}

@register_tool("calculate_fire")
async def calculate_fire(
    user_age: int = 30,
    current_savings: int = 10000,
    monthly_income: int = 5000,
    monthly_expenses: int = 4000,
    target_retirement_age: int = 45,
    risk_tolerance: str = "moderate"
) -> Dict[str, Any]:
    """
    💀 BRUTAL FIRE CALCULATOR: Calculate Financial Independence Retire Early (FIRE) requirements 
    with brutal honesty about reality. Shows exactly how much user needs to invest monthly.
    """
    try:
        # Calculate savings rate
        monthly_savings = monthly_income - monthly_expenses
        savings_rate = monthly_savings / monthly_income if monthly_income > 0 else 0
        
        # FIRE number (25x annual expenses for 4% rule)
        annual_expenses = monthly_expenses * 12
        fire_number = annual_expenses * 25
        
        # Years to retirement
        years_to_retirement = target_retirement_age - user_age
        
        # Return assumptions based on risk tolerance
        if risk_tolerance == "conservative":
            annual_return = 0.06
        elif risk_tolerance == "moderate":
            annual_return = 0.07
        else:  # aggressive
            annual_return = 0.08
        
        # Calculate required monthly investment
        monthly_return = annual_return / 12
        months_to_retirement = years_to_retirement * 12
        
        # Future value of current savings
        future_value_current = current_savings * ((1 + annual_return) ** years_to_retirement)
        
        # Required additional investment
        required_additional = fire_number - future_value_current
        
        # Monthly payment calculation (PMT formula)
        if months_to_retirement > 0:
            monthly_required = (required_additional * monthly_return) / (((1 + monthly_return) ** months_to_retirement) - 1)
        else:
            monthly_required = 0
        
        # Reality check with brutal honesty
        reality_check = ""
        feasibility = "FEASIBLE"
        
        if monthly_required > monthly_income * 0.7:
            reality_check = f"💀 BRUTAL REALITY: You need ${monthly_required:,.0f}/month to retire at {target_retirement_age}. That's {(monthly_required/monthly_income)*100:.0f}% of your income. Either earn more or retire later."
            feasibility = "IMPOSSIBLE"
        elif monthly_required > monthly_income * 0.5:
            reality_check = f"⚠️ AGGRESSIVE BUT POSSIBLE: You need ${monthly_required:,.0f}/month to retire at {target_retirement_age}. That's {(monthly_required/monthly_income)*100:.0f}% of your income. This requires serious lifestyle changes."
            feasibility = "AGGRESSIVE"
        elif monthly_required > monthly_savings:
            reality_check = f"📈 CHALLENGING: You need ${monthly_required:,.0f}/month but only save ${monthly_savings:,.0f}. Increase savings by ${monthly_required - monthly_savings:,.0f}/month."
            feasibility = "CHALLENGING"
        else:
            reality_check = f"✅ FEASIBLE: You're on track! Need ${monthly_required:,.0f}/month and you save ${monthly_savings:,.0f}. FIRE at {target_retirement_age} is realistic."
            feasibility = "FEASIBLE"
        
        # Alternative scenarios
        scenarios = []
        
        # Scenario 1: Retire at 50
        alt_years = 50 - user_age
        if alt_years > 0:
            alt_future_value = current_savings * ((1 + annual_return) ** alt_years)
            alt_required = (fire_number - alt_future_value) * monthly_return / (((1 + monthly_return) ** (alt_years * 12)) - 1)
            scenarios.append({
                "retirement_age": 50,
                "monthly_required": alt_required,
                "feasible": alt_required <= monthly_income * 0.4,
                "percentage_of_income": (alt_required / monthly_income) * 100
            })
        
        # Scenario 2: Retire at 60
        alt_years = 60 - user_age
        if alt_years > 0:
            alt_future_value = current_savings * ((1 + annual_return) ** alt_years)
            alt_required = (fire_number - alt_future_value) * monthly_return / (((1 + monthly_return) ** (alt_years * 12)) - 1)
            scenarios.append({
                "retirement_age": 60,
                "monthly_required": alt_required,
                "feasible": alt_required <= monthly_income * 0.3,
                "percentage_of_income": (alt_required / monthly_income) * 100
            })
        
        # Generate recommendations based on feasibility
        recommendations = []
        
        if feasibility == "IMPOSSIBLE":
            recommendations.extend([
                "Increase income through side hustles, career advancement, or job change",
                "Consider retiring later (50-55 instead of 45)",
                "Reduce expenses significantly",
                "Move to lower cost of living area"
            ])
        elif feasibility == "AGGRESSIVE":
            recommendations.extend([
                "Cut expenses by 20-30%",
                "Increase income through side hustles",
                "Consider semi-retirement instead of full FIRE",
                "Optimize tax strategies (401k, IRA, HSA)"
            ])
        elif feasibility == "CHALLENGING":
            recommendations.extend([
                "Increase savings rate gradually",
                "Look for ways to reduce expenses",
                "Consider higher return investments if risk tolerance allows",
                "Track spending to find optimization opportunities"
            ])
        else:  # FEASIBLE
            recommendations.extend([
                "Stay the course - you're on track",
                "Consider increasing savings for earlier retirement",
                "Optimize investment allocation",
                "Plan for healthcare costs in retirement"
            ])
        
        return {
            "fire_calculation": {
                "fire_number": fire_number,
                "current_savings": current_savings,
                "monthly_income": monthly_income,
                "monthly_expenses": monthly_expenses,
                "monthly_savings": monthly_savings,
                "savings_rate": savings_rate,
                "target_retirement_age": target_retirement_age,
                "years_to_retirement": years_to_retirement
            },
            "required_investment": {
                "monthly_required": monthly_required,
                "annual_required": monthly_required * 12,
                "percentage_of_income": (monthly_required / monthly_income) * 100 if monthly_income > 0 else 0,
                "annual_return_assumption": annual_return,
                "feasibility": feasibility
            },
            "reality_check": reality_check,
            "alternative_scenarios": scenarios,
            "recommendations": recommendations
        }
        
    except Exception as e:
        print(f"❌ Error calculating FIRE: {e}")
        return {"error": str(e)}

@register_tool("negotiate_access")
async def negotiate_access(
    user_profile: Dict[str, Any] = None,
    initial_request: str = "I want to use your financial advisor",
    conversation_stage: str = "initial"
) -> Dict[str, Any]:
    """
    🤝 NEGOTIATION SYSTEM: User must convince AI to work with them and negotiate pricing.
    AI analyzes user profile and sets conditions. Production-grade conversation flow.
    """
    try:
        if not user_profile:
            user_profile = {
                "age": 30,
                "income": 50000,
                "savings": 10000,
                "investment_experience": "beginner",
                "risk_tolerance": "moderate",
                "goals": "financial independence",
                "conversation_stage": "initial"
            }
        
        # Analyze user profile
        savings_rate = user_profile["savings"] / user_profile["income"] if user_profile["income"] > 0 else 0
        age = user_profile["age"]
        income = user_profile["income"]
        savings = user_profile["savings"]
        
        # Production-grade conversation flow
        if conversation_stage == "initial":
            # First interaction - ask qualifying questions
            questions = [
                "What's your biggest financial goal? (FIRE, house down payment, debt payoff, etc.)",
                "How much do you currently save each month?",
                "What's your risk tolerance? (Conservative, Moderate, Aggressive)",
                "What's your investment experience level? (Beginner, Intermediate, Advanced)",
                "What's your timeline for achieving your financial goals?"
            ]
            
            return {
                "conversation_stage": "qualifying",
                "response": "I'm not just any financial advisor - I'm an aggressive FIRE coach who roasts portfolios and demands commitment.\n\nBefore we talk pricing, I need to understand your financial situation and goals. Answer these questions honestly:",
                "questions": questions,
                "next_steps": "User answers qualifying questions"
            }
        
        elif conversation_stage == "qualifying":
            # Analyze answers and give initial assessment
            assessment = ""
            base_price = 199
            
            # Financial situation analysis
            if savings_rate < 0.05:
                assessment = "You save less than 5%? This is going to be expensive. You need lifestyle changes, not just investment advice."
                base_price = 299
            elif savings_rate < 0.15:
                assessment = "15% savings rate is better, but still not enough for aggressive FIRE. We need to push harder."
                base_price = 249
            elif savings_rate >= 0.25:
                assessment = "25%+ savings rate? Respect. You're serious about FIRE. I can work with this."
                base_price = 149
            
            # Age-based analysis
            if age > 50 and savings < 100000:
                assessment += f" You're {age} with less than $100K saved. Time to get aggressive or work longer."
                base_price = max(base_price, 299)
            elif age < 25 and savings > 10000:
                assessment += " Young with decent savings. You have time on your side - let's use it."
                base_price = 99
            
            # Experience-based pricing
            if user_profile["investment_experience"] == "beginner":
                assessment += " Beginner investor. I'll need to educate you first."
                base_price = max(base_price - 50, 99)
            elif user_profile["investment_experience"] == "advanced":
                assessment += " Advanced investor. We can focus on optimization and tax strategies."
                base_price += 50
            
            return {
                "conversation_stage": "assessment",
                "response": f"{assessment}\n\nBased on your profile, my base rate is ${base_price}/month. But I don't work with everyone.\n\nWhat's your budget for financial advice?",
                "pricing": {
                    "base_price": base_price,
                    "reasoning": "Profile-based pricing"
                },
                "next_steps": "User provides budget counter-offer"
            }
        
        elif conversation_stage == "budget_negotiation":
            # Handle budget counter-offers
            user_budget = user_profile.get("budget", 100)
            base_price = user_profile.get("base_price", 199)
            
            if user_budget < 50:
                return {
                    "conversation_stage": "rejected",
                    "response": "Less than $50/month? I don't work with people who aren't serious about their finances. Come back when you're ready to invest in your future.",
                    "access_granted": False,
                    "reason": "Budget too low"
                }
            elif user_budget < base_price * 0.7:
                return {
                    "conversation_stage": "counter_offer",
                    "response": f"${user_budget}/month is low for the value I provide. I'll do ${base_price * 0.8:.0f}/month if you commit to my 3 rules:\n\n1. Save 25% minimum\n2. No meme stocks\n3. Follow my FIRE plan religiously\n\nDeal?",
                    "counter_offer": base_price * 0.8,
                    "conditions": [
                        "Save 25% minimum",
                        "No meme stocks", 
                        "Follow FIRE plan religiously"
                    ]
                }
            else:
                return {
                    "conversation_stage": "accepted",
                    "response": f"${user_budget}/month works. Welcome to aggressive FIRE coaching.\n\nMy conditions:\n1. Save 25% minimum\n2. No meme stocks\n3. Follow my FIRE plan religiously\n4. Weekly check-ins\n\nReady to get started?",
                    "final_price": user_budget,
                    "conditions": [
                        "Save 25% minimum",
                        "No meme stocks",
                        "Follow FIRE plan religiously", 
                        "Weekly check-ins"
                    ],
                    "access_granted": True
                }
        
        elif conversation_stage == "final_agreement":
            # Final agreement and onboarding
            return {
                "conversation_stage": "onboarding",
                "response": "Perfect! Let's get started with your FIRE journey.\n\nFirst, I need to see your current portfolio. Connect your brokerage account or tell me about your current investments.\n\nThen we'll:\n1. Roast your portfolio (prepare for brutal honesty)\n2. Calculate your FIRE number\n3. Create an aggressive savings plan\n4. Set up weekly check-ins\n\nReady to begin?",
                "onboarding_steps": [
                    "Connect brokerage account",
                    "Portfolio analysis and roast",
                    "FIRE calculation",
                    "Savings plan creation",
                    "Weekly check-in setup"
                ],
                "access_granted": True
            }
        
        # Default fallback
        return {
            "conversation_stage": "error",
            "response": "I'm not sure what stage we're in. Let's start over - what's your biggest financial goal?",
            "next_steps": "Restart conversation"
        }
        
    except Exception as e:
        print(f"❌ Error negotiating access: {e}")
        return {"error": str(e)}

@register_tool("assess_risk_tolerance")
async def assess_risk_tolerance(
    user_responses: Dict[str, Any] = None,
    conversation_stage: str = "initial"
) -> Dict[str, Any]:
    """
    🎯 RISK TOLERANCE ASSESSMENT: Comprehensive questionnaire to understand user's risk appetite
    and recommend appropriate investment strategies (index funds, ETFs, stocks, options).
    """
    try:
        if conversation_stage == "initial":
            # Initial risk assessment questions
            questions = [
                {
                    "id": "investment_experience",
                    "question": "What's your investment experience level?",
                    "options": [
                        {"value": "beginner", "text": "Beginner - I'm new to investing"},
                        {"value": "intermediate", "text": "Intermediate - I understand basics"},
                        {"value": "advanced", "text": "Advanced - I actively manage my portfolio"}
                    ]
                },
                {
                    "id": "time_horizon",
                    "question": "What's your primary investment timeline?",
                    "options": [
                        {"value": "short", "text": "1-3 years (short-term goals)"},
                        {"value": "medium", "text": "3-10 years (medium-term)"},
                        {"value": "long", "text": "10+ years (long-term/FIRE)"}
                    ]
                },
                {
                    "id": "volatility_tolerance",
                    "question": "How would you react to a 20% portfolio drop?",
                    "options": [
                        {"value": "panic_sell", "text": "Sell everything - I can't handle losses"},
                        {"value": "concerned", "text": "Worry but hold on"},
                        {"value": "opportunity", "text": "See it as a buying opportunity"}
                    ]
                },
                {
                    "id": "investment_goals",
                    "question": "What's your primary investment goal?",
                    "options": [
                        {"value": "preserve", "text": "Preserve capital with steady growth"},
                        {"value": "moderate_growth", "text": "Moderate growth with some risk"},
                        {"value": "aggressive_growth", "text": "Aggressive growth - high risk, high reward"}
                    ]
                },
                {
                    "id": "financial_stability",
                    "question": "How stable is your income?",
                    "options": [
                        {"value": "unstable", "text": "Variable/unstable income"},
                        {"value": "stable", "text": "Stable salary/wage"},
                        {"value": "very_stable", "text": "Very stable with emergency fund"}
                    ]
                }
            ]
            
            return {
                "conversation_stage": "risk_assessment",
                "response": "I need to understand your risk tolerance to give you the right recommendations.\n\nAnswer these questions honestly - there are no wrong answers. This helps me recommend the right mix of index funds, ETFs, individual stocks, or options for your situation.",
                "questions": questions,
                "next_steps": "User answers risk assessment questions"
            }
        
        elif conversation_stage == "risk_assessment" and user_responses:
            # Analyze responses and determine risk profile
            experience = user_responses.get("investment_experience", "beginner")
            time_horizon = user_responses.get("time_horizon", "medium")
            volatility_tolerance = user_responses.get("volatility_tolerance", "concerned")
            goals = user_responses.get("investment_goals", "moderate_growth")
            stability = user_responses.get("financial_stability", "stable")
            
            # Calculate risk score (1-10)
            risk_score = 5  # Start neutral
            
            # Experience factor
            if experience == "beginner":
                risk_score -= 2
            elif experience == "advanced":
                risk_score += 2
            
            # Time horizon factor
            if time_horizon == "short":
                risk_score -= 2
            elif time_horizon == "long":
                risk_score += 1
            
            # Volatility tolerance factor
            if volatility_tolerance == "panic_sell":
                risk_score -= 3
            elif volatility_tolerance == "opportunity":
                risk_score += 2
            
            # Goals factor
            if goals == "preserve":
                risk_score -= 2
            elif goals == "aggressive_growth":
                risk_score += 2
            
            # Stability factor
            if stability == "unstable":
                risk_score -= 1
            
            # Clamp risk score to 1-10
            risk_score = max(1, min(10, risk_score))
            
            # Determine risk profile
            if risk_score <= 3:
                risk_profile = "Conservative"
                recommendation_type = "Index Funds & ETFs"
                recommended_allocations = {
                    "bonds": 40,
                    "index_funds": 50,
                    "stocks": 10,
                    "options": 0
                }
                description = "You prefer capital preservation over growth. Index funds and ETFs are perfect for you."
            elif risk_score <= 6:
                risk_profile = "Moderate"
                recommendation_type = "Balanced Portfolio"
                recommended_allocations = {
                    "bonds": 20,
                    "index_funds": 50,
                    "stocks": 25,
                    "options": 5
                }
                description = "You can handle some volatility for better returns. A balanced approach works well."
            else:
                risk_profile = "Aggressive"
                recommendation_type = "Growth-Focused"
                recommended_allocations = {
                    "bonds": 10,
                    "index_funds": 30,
                    "stocks": 50,
                    "options": 10
                }
                description = "You're comfortable with risk for higher returns. Individual stocks and options can be part of your strategy."
            
            # Generate specific recommendations
            recommendations = []
            
            if risk_score <= 3:
                recommendations.extend([
                    "Focus on VTI (Total Stock Market) and BND (Bonds) ETFs",
                    "Consider target-date funds for set-and-forget investing",
                    "Avoid individual stocks and options completely",
                    "Rebalance quarterly to maintain allocation"
                ])
            elif risk_score <= 6:
                recommendations.extend([
                    "Core holding: VTI + VXUS (Total World Stock Market)",
                    "Add some individual blue-chip stocks (AAPL, MSFT, GOOGL)",
                    "Consider covered calls on your stock positions",
                    "Keep emergency fund in high-yield savings"
                ])
            else:
                recommendations.extend([
                    "Build concentrated positions in high-conviction stocks",
                    "Use options for income (covered calls, cash-secured puts)",
                    "Consider growth stocks and sector ETFs",
                    "Active management and regular rebalancing"
                ])
            
            return {
                "conversation_stage": "risk_profile_complete",
                "risk_assessment": {
                    "risk_score": risk_score,
                    "risk_profile": risk_profile,
                    "recommendation_type": recommendation_type,
                    "description": description,
                    "recommended_allocations": recommended_allocations
                },
                "response": f"Based on your answers, you're a **{risk_profile}** investor with a risk score of **{risk_score}/10**.\n\n**Your Profile**: {description}\n\n**Recommended Strategy**: {recommendation_type}\n\n**Suggested Allocation**:\n• Bonds: {recommended_allocations['bonds']}%\n• Index Funds: {recommended_allocations['index_funds']}%\n• Individual Stocks: {recommended_allocations['stocks']}%\n• Options: {recommended_allocations['options']}%",
                "recommendations": recommendations,
                "next_steps": "Use this risk profile for portfolio recommendations and FIRE calculations"
            }
        
        else:
            return {
                "conversation_stage": "error",
                "response": "I need more information to assess your risk tolerance. Let's start over with the risk assessment questions.",
                "next_steps": "Restart risk assessment"
            }
        
    except Exception as e:
        print(f"❌ Error assessing risk tolerance: {e}")
        return {"error": str(e)}

@register_tool("connect_brokerage")
async def connect_brokerage(
    user_id: str = None,
    redirect_uri: str = "http://localhost:8787/callback"
) -> Dict[str, Any]:
    """
    🏦 BROKERAGE CONNECTION: Connect user's Robinhood or other brokerage account
    via SnapTrade for real portfolio data analysis.
    """
    try:
        if not user_id:
            user_id = f"user_{random.randint(100000, 999999)}"
        
        # Create SnapTrade user
        user_result = await snaptrade_client.create_user(user_id)
        
        if user_result.get("error"):
            return {
                "success": False,
                "error": user_result["error"],
                "message": "Failed to create SnapTrade user account"
            }
        
        # Generate connection portal URL
        connection_result = await snaptrade_client.get_connection_portal_url(
            user_id=user_result["userId"],
            user_secret=user_result["userSecret"],
            redirect_uri=redirect_uri
        )
        
        if connection_result.get("error"):
            return {
                "success": False,
                "error": connection_result["error"],
                "message": "Failed to generate connection URL"
            }
        
        return {
            "success": True,
            "user_id": user_result["userId"],
            "user_secret": user_result["userSecret"],
            "connection_url": connection_result["redirect_url"],
            "message": "Click the connection URL to link your brokerage account",
            "instructions": [
                "1. Click the connection URL to open SnapTrade portal",
                "2. Select your brokerage (Robinhood, TD Ameritrade, etc.)",
                "3. Enter your brokerage login credentials",
                "4. Authorize SnapTrade to access your account",
                "5. Return to chat for portfolio analysis"
            ]
        }
        
    except Exception as e:
        print(f"❌ Error connecting brokerage: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to initiate brokerage connection"
        }

@register_tool("get_real_portfolio")
async def get_real_portfolio(
    user_id: str,
    user_secret: str,
    account_id: str = None
) -> Dict[str, Any]:
    """
    📊 REAL PORTFOLIO DATA: Fetch user's actual portfolio from connected brokerage
    for authentic portfolio roasting and FIRE calculations.
    """
    try:
        # Get user accounts
        accounts = await snaptrade_client.get_user_accounts(user_id, user_secret)
        
        if not accounts:
            return {
                "success": False,
                "message": "No connected accounts found. Please connect your brokerage first.",
                "accounts": []
            }
        
        # Use first account if none specified
        if not account_id:
            account_id = accounts[0]["id"]
        
        # Get positions and balances
        positions = await snaptrade_client.get_account_positions(user_id, user_secret, account_id)
        balances = await snaptrade_client.get_account_balances(user_id, user_secret, account_id)
        
        # Calculate portfolio metrics
        total_invested = sum(pos.get("cost_basis", 0) for pos in positions)
        total_current = sum(pos.get("market_value", 0) for pos in positions)
        total_pnl = total_current - total_invested
        pnl_percent = (total_pnl / total_invested * 100) if total_invested else 0
        
        return {
            "success": True,
            "account_id": account_id,
            "accounts": accounts,
            "positions": positions,
            "balances": balances,
            "portfolio_summary": {
                "total_invested": total_invested,
                "total_current": total_current,
                "total_pnl": total_pnl,
                "pnl_percent": pnl_percent,
                "cash": balances.get("cash", 0),
                "total_equity": balances.get("total_equity", total_current)
            },
            "message": "Real portfolio data fetched successfully"
        }
        
    except Exception as e:
        print(f"❌ Error getting real portfolio: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to fetch portfolio data"
        }

@register_tool("analyze_robinhood_portfolio")
async def analyze_robinhood_portfolio(
    access_token: str,
    account_id: str = None
) -> Dict[str, Any]:
    """
    📊 ROBINHOOD PORTFOLIO ANALYSIS: Fetch and analyze user's actual Robinhood portfolio
    for authentic portfolio roasting and FIRE calculations using real data.
    """
    try:
        # Get accounts
        accounts_result = await robinhood_client.get_accounts(access_token)
        if not accounts_result.get("success"):
            return {
                "success": False,
                "error": accounts_result.get("error", "Failed to get accounts"),
                "message": "Could not access Robinhood accounts"
            }
        
        accounts = accounts_result.get("accounts", [])
        if not accounts:
            return {
                "success": False,
                "error": "No accounts found",
                "message": "No Robinhood accounts found"
            }
        
        # Use first account if none specified
        if not account_id:
            account_id = accounts[0].get("account_number")
        
        # Get positions and portfolio data
        positions_result = await robinhood_client.get_positions(access_token, account_id)
        portfolio_result = await robinhood_client.get_portfolios(access_token, account_id)
        
        positions = positions_result.get("positions", []) if positions_result.get("success") else []
        portfolios = portfolio_result.get("portfolios", []) if portfolio_result.get("success") else []
        
        # Filter out zero positions
        active_positions = [pos for pos in positions if float(pos.get("quantity", 0)) > 0]
        
        # Calculate portfolio metrics
        total_equity = 0
        total_market_value = 0
        total_cost_basis = 0
        
        if portfolios:
            portfolio = portfolios[0] if isinstance(portfolios, list) else portfolios
            total_equity = float(portfolio.get("equity", 0))
            total_market_value = float(portfolio.get("market_value", 0))
            total_cost_basis = float(portfolio.get("extended_hours_equity", 0))
        
        # Calculate P&L
        total_pnl = total_equity - total_cost_basis
        pnl_percent = (total_pnl / total_cost_basis * 100) if total_cost_basis > 0 else 0
        
        # Get market data for symbols
        symbols = [pos.get("instrument", "").split("/")[-2] for pos in active_positions if pos.get("instrument")]
        market_data = {}
        if symbols:
            market_result = await robinhood_client.get_market_data(symbols)
            if market_result.get("success"):
                quotes = market_result.get("quotes", [])
                market_data = {quote.get("symbol"): quote for quote in quotes}
        
        # Format positions with real data
        formatted_positions = []
        for pos in active_positions:
            symbol = pos.get("instrument", "").split("/")[-2] if pos.get("instrument") else "UNKNOWN"
            quantity = float(pos.get("quantity", 0))
            avg_cost = float(pos.get("average_buy_price", 0))
            current_price = 0
            
            if symbol in market_data:
                current_price = float(market_data[symbol].get("last_trade_price", 0))
            elif avg_cost > 0:
                current_price = avg_cost  # Fallback to cost basis
            
            market_value = quantity * current_price
            cost_basis = quantity * avg_cost
            unrealized_pl = market_value - cost_basis
            unrealized_pl_percent = (unrealized_pl / cost_basis * 100) if cost_basis > 0 else 0
            
            formatted_positions.append({
                "symbol": symbol,
                "shares": quantity,
                "current_price": current_price,
                "market_value": market_value,
                "cost_basis": cost_basis,
                "unrealized_pl": unrealized_pl,
                "unrealized_pl_percent": unrealized_pl_percent
            })
        
        return {
            "success": True,
            "account_id": account_id,
            "accounts": accounts,
            "positions": formatted_positions,
            "portfolio_summary": {
                "total_equity": total_equity,
                "total_market_value": total_market_value,
                "total_cost_basis": total_cost_basis,
                "total_pnl": total_pnl,
                "pnl_percent": pnl_percent,
                "cash": float(accounts[0].get("cash", 0)) if accounts else 0
            },
            "market_data": market_data,
            "message": "Real Robinhood portfolio data fetched successfully"
        }
        
    except Exception as e:
        print(f"❌ Error analyzing Robinhood portfolio: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to analyze Robinhood portfolio"
        }
