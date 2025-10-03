from crewai import Agent
from tools.custom_tools import CodeInterpreterTool
from tools.custom_tools import monte_carlo_simulation_tool, monte_carlo_results_explainer
from config import config
import streamlit as st

class SimulateAgent:
    """Agent responsible for Monte Carlo simulation and scenario analysis"""
    
    @staticmethod
    def create_agent():
        # Get current model configuration with validation
        selected_model = config.validate_and_fix_selected_model()
        model_config = config.AVAILABLE_MODELS[selected_model]
        provider = model_config['provider']
        
        # Set up LLM based on provider
        llm = None
        if provider == 'openai':
            from crewai.llm import LLM
            llm = LLM(
                model=f"openai/{selected_model}",
                api_key=config.OPENAI_API_KEY,
                temperature=config.TEMPERATURE
            )
        elif provider == 'anthropic':
            from crewai.llm import LLM
            llm = LLM(
                model=f"anthropic/{selected_model}",
                api_key=config.ANTHROPIC_API_KEY,
                temperature=config.TEMPERATURE
            )
        
        return Agent(
            role="Quantitative Analysis and Simulation Specialist",
            goal="Conduct Monte Carlo simulations to model optimistic, baseline, and pessimistic scenarios with statistical analysis",
            backstory="""You are a quantitative analyst and simulation expert with deep expertise in Monte Carlo 
            methods, statistical modeling, and scenario analysis. You excel at translating business assumptions 
            into mathematical models, running sophisticated simulations, and interpreting results for strategic 
            decision-making. Your expertise includes risk modeling, probability distributions, sensitivity analysis, 
            and statistical visualization.""",
            tools=[
                monte_carlo_simulation_tool,
                monte_carlo_results_explainer,
                CodeInterpreterTool()
            ],
            verbose=True,
            allow_delegation=False,
            max_iter=config.MAX_ITERATIONS,
            temperature=config.TEMPERATURE,
            llm=llm
        )
    
    @staticmethod
    def create_task(implementation_plan: str, option_analysis: str):
        from crewai import Task
        return Task(
            description = f"""
            Conduct comprehensive Monte Carlo simulation analysis for the implementation plan and strategic option.
            
            Implementation Plan:
            {implementation_plan}
            
            Strategic Option Analysis:
            {option_analysis}
            
            Simulation Requirements:
            1. **Model Development**
               - Extract key variables and parameters from implementation plan
               - Define probability distributions for uncertain factors
               - Create mathematical models for outcomes
               - Establish correlations between variables
               
            2. **Scenario Configuration**
               - Design optimistic scenario (90th percentile outcomes)
               - Design baseline scenario (50th percentile outcomes)
               - Design pessimistic scenario (10th percentile outcomes)
               - Define scenario-specific assumptions and constraints
               
            3. **Monte Carlo Simulation Execution**
               - Run minimum 1000 simulation iterations
               - Generate probability distributions for key outcomes
               - Calculate statistical measures and confidence intervals
               - Perform sensitivity analysis on key variables
               
            4. **Risk Analysis**
               - Quantify downside risks and upside potential
               - Calculate Value at Risk (VaR) metrics
               - Identify key risk drivers and uncertainties
               - Assess probability of achieving target outcomes
               
            5. **Visualization and Reporting**
               - Create charts and graphs for scenario comparison
               - Generate statistical summaries and distributions
               - Develop executive summary with key insights
               - Provide actionable recommendations based on results
            
            Run comprehensive simulations with {config.MONTE_CARLO_RUNS} iterations and provide detailed statistical analysis.
            """,
            expected_output = """A comprehensive Monte Carlo simulation analysis document containing:
            
            # Monte Carlo Simulation Analysis Report
            
            ## Executive Summary
            - **Simulation Overview**: [Scope and methodology of analysis]
            - **Key Findings**: [Top 5 insights from simulation results]
            - **Recommended Scenario**: [Most likely outcome scenario]
            - **Risk Assessment**: [Overall risk profile and recommendations]
            - **Decision Confidence**: [Statistical confidence in projections]
            
            ## Simulation Methodology
            
            ### Model Architecture
            #### Variable Identification
            **Key Input Variables:**
            1. **Variable 1**: [Name and description]
               - **Distribution Type**: [Normal, Beta, Triangular, etc.]
               - **Parameters**: [Mean, standard deviation, min/max values]
               - **Justification**: [Why this distribution was chosen]
            
            2. **Variable 2**: [Second key variable]
            3. **Variable 3**: [Third key variable]
            
            **Key Output Variables:**
            - **Primary Outcome**: [Main metric being simulated]
            - **Secondary Outcomes**: [Supporting metrics]
            - **Risk Metrics**: [Risk-related outputs]
            
            #### Model Structure
            - **Mathematical Relationships**: [How variables relate to each other]
            - **Correlation Assumptions**: [Variable interdependencies]
            - **Model Limitations**: [Assumptions and constraints]
            - **Validation Approach**: [How model accuracy was verified]
            
            ### Simulation Configuration
            #### Technical Parameters
            - **Simulation Runs**: [Number of iterations performed]
            - **Random Seed**: [For result reproducibility]
            - **Convergence Criteria**: [How stability was ensured]
            - **Computing Environment**: [Technical setup details]
            
            #### Scenario Design Framework
            - **Optimistic Scenario Logic**: [Assumptions for best-case]
            - **Baseline Scenario Logic**: [Assumptions for expected case]
            - **Pessimistic Scenario Logic**: [Assumptions for worst-case]
            
            ## Scenario Analysis Results
            
            ### Optimistic Scenario (90th Percentile)
            #### Scenario Assumptions
            - **Market Conditions**: [Favorable market assumptions]
            - **Internal Performance**: [High-performance assumptions]
            - **External Factors**: [Positive external factor assumptions]
            - **Resource Availability**: [Optimal resource assumptions]
            
            #### Key Results
            - **Primary Outcome**: [90th percentile result with confidence interval]
            - **Timeline Achievement**: [Schedule performance in optimistic case]
            - **Resource Utilization**: [Resource efficiency in best case]
            - **Risk Materialization**: [Probability of risks occurring]
            
            #### Success Probability
            - **Target Achievement Probability**: [Likelihood of meeting/exceeding targets]
            - **Value Creation Potential**: [Maximum value that could be created]
            - **Competitive Advantage**: [Advantage gained in best case]
            
            ### Baseline Scenario (50th Percentile)
            #### Scenario Assumptions
            - **Market Conditions**: [Expected market conditions]
            - **Internal Performance**: [Expected performance levels]
            - **External Factors**: [Neutral external factor assumptions]
            - **Resource Availability**: [Expected resource availability]
            
            #### Key Results
            - **Primary Outcome**: [Median result with confidence interval]
            - **Timeline Achievement**: [Expected schedule performance]
            - **Resource Utilization**: [Expected resource efficiency]
            - **Risk Materialization**: [Expected risk occurrence]
            
            #### Most Likely Outcomes
            - **Expected Value**: [Mean expected outcome]
            - **Performance Range**: [Likely performance corridor]
            - **Risk-Adjusted Returns**: [Risk-adjusted performance expectations]
            
            ### Pessimistic Scenario (10th Percentile)
            #### Scenario Assumptions
            - **Market Conditions**: [Adverse market assumptions]
            - **Internal Performance**: [Challenged performance assumptions]
            - **External Factors**: [Negative external factor assumptions]
            - **Resource Availability**: [Constrained resource assumptions]
            
            #### Key Results
            - **Primary Outcome**: [10th percentile result with confidence interval]
            - **Timeline Achievement**: [Schedule performance in adverse case]
            - **Resource Utilization**: [Resource efficiency in worst case]
            - **Risk Materialization**: [High probability risks]
            
            #### Downside Protection
            - **Minimum Expected Outcome**: [Worst reasonably expected result]
            - **Failure Probability**: [Likelihood of significant underperformance]
            - **Mitigation Requirements**: [Actions needed to avoid worst case]
            
            ## Statistical Analysis and Results
            
            ### Probability Distribution Analysis
            #### Primary Outcome Distribution
            - **Distribution Shape**: [Normal, skewed, bimodal, etc.]
            - **Central Tendency**: [Mean, median, mode]
            - **Variability**: [Standard deviation, variance, range]
            - **Skewness and Kurtosis**: [Distribution characteristics]
            
            #### Percentile Analysis
            | Percentile | Outcome Value | Probability of Exceeding |
            |------------|---------------|-------------------------|
            | 10th | [Value] | 90% |
            | 25th | [Value] | 75% |
            | 50th | [Value] | 50% |
            | 75th | [Value] | 25% |
            | 90th | [Value] | 10% |
            | 95th | [Value] | 5% |
            
            ### Risk Metrics and Analysis
            #### Value at Risk (VaR) Analysis
            - **VaR (5%)**: [Maximum loss with 5% probability]
            - **VaR (10%)**: [Maximum loss with 10% probability]
            - **Expected Shortfall**: [Average loss beyond VaR threshold]
            - **Maximum Drawdown**: [Worst-case scenario outcome]
            
            #### Risk-Return Profile
            - **Expected Return**: [Mean expected outcome]
            - **Volatility**: [Standard deviation of outcomes]
            - **Sharpe Ratio**: [Risk-adjusted return measure]
            - **Probability of Loss**: [Likelihood of negative outcomes]
            
            ### Sensitivity Analysis
            #### Key Sensitivity Drivers
            1. **Variable 1 Sensitivity**: [Impact of changes in key variable]
               - **Impact Magnitude**: [How much outcome changes]
               - **Elasticity**: [Percentage change relationship]
               - **Critical Thresholds**: [Break-even points]
            
            2. **Variable 2 Sensitivity**: [Second most important driver]
            3. **Variable 3 Sensitivity**: [Third most important driver]
            
            #### Tornado Diagram Results
            [Ranking of variables by impact on outcome variance]
            - **Most Influential**: [Variables with highest impact]
            - **Medium Influence**: [Moderately important variables]
            - **Low Influence**: [Variables with minimal impact]
            
            ## Scenario Comparison and Analysis
            
            ### Cross-Scenario Comparison
            | Metric | Optimistic | Baseline | Pessimistic | Range |
            |--------|------------|----------|-------------|-------|
            | **Primary Outcome** | [Value] | [Value] | [Value] | [Range] |
            | **Timeline** | [Duration] | [Duration] | [Duration] | [Range] |
            | **Budget Performance** | [%] | [%] | [%] | [Range] |
            | **ROI** | [%] | [%] | [%] | [Range] |
            | **Risk Score** | [Score] | [Score] | [Score] | [Range] |
            
            ### Scenario Probability Assessment
            - **Optimistic Scenario Likelihood**: [Probability of achieving]
            - **Baseline Scenario Likelihood**: [Probability of achieving]
            - **Pessimistic Scenario Likelihood**: [Probability of occurrence]
            - **Extreme Outcome Probabilities**: [Very high/low outcome chances]
            
            ### Decision Support Analysis
            #### Risk-Adjusted Recommendations
            - **Conservative Strategy**: [Recommendation for risk-averse approach]
            - **Balanced Strategy**: [Recommendation for moderate risk tolerance]
            - **Aggressive Strategy**: [Recommendation for high risk tolerance]
            
            #### Threshold Analysis
            - **Break-Even Points**: [Minimum performance for viability]
            - **Target Achievement Probability**: [Likelihood of meeting objectives]
            - **Acceptable Risk Range**: [Risk levels within tolerance]
            
            ## Monte Carlo Simulation Charts and Visualizations
            
            ### Distribution Charts
            #### Primary Outcome Probability Distribution
            ```
            [Description of histogram/density plot showing outcome distribution]
            - X-axis: Outcome values
            - Y-axis: Probability density
            - Key features: Mean, percentiles, confidence intervals
            ```
            
            #### Cumulative Probability Chart
            ```
            [Description of cumulative distribution function]
            - Shows probability of achieving any given outcome level
            - Key percentiles marked
            - Risk thresholds highlighted
            ```
            
            ### Scenario Comparison Charts
            #### Box Plot Comparison
            ```
            [Description of box plots comparing three scenarios]
            - Shows median, quartiles, and outliers for each scenario
            - Enables visual comparison of distributions
            ```
            
            #### Tornado Chart - Sensitivity Analysis
            ```
            [Description of tornado chart showing variable sensitivities]
            - Horizontal bars showing impact of each variable
            - Ranked by magnitude of impact
            ```
            
            ### Time Series Analysis
            #### Outcome Evolution Over Time
            ```
            [Description of time series showing how outcomes evolve]
            - Multiple scenario trajectories
            - Confidence bands around projections
            ```
            
            ## Risk Analysis and Mitigation Insights
            
            ### High-Impact Risk Factors
            #### Top Risk Drivers
            1. **Risk Factor 1**: [Highest impact uncertainty]
               - **Impact on Outcomes**: [Quantified impact]
               - **Probability Range**: [Likelihood of occurrence]
               - **Mitigation Strategies**: [How to reduce impact]
               - **Monitoring Indicators**: [Early warning signals]
            
            2. **Risk Factor 2**: [Second highest impact]
            3. **Risk Factor 3**: [Third highest impact]
            
            ### Risk Mitigation Prioritization
            #### Immediate Attention Required
            - **High Probability, High Impact**: [Risks needing immediate action]
            - **Mitigation ROI**: [Most cost-effective risk reductions]
            - **Quick Wins**: [Easy-to-implement risk reductions]
            
            ### Contingency Planning Insights
            #### Scenario-Based Contingencies
            - **If Pessimistic Trends Emerge**: [Early response strategies]
            - **If Optimistic Conditions Arise**: [Opportunity maximization strategies]
            - **Critical Decision Points**: [When to change course]
            
            ## Strategic Recommendations
            
            ### Primary Recommendations
            #### Go/No-Go Decision Support
            - **Recommendation**: [Go/No-Go with confidence level]
            - **Statistical Justification**: [Quantitative basis for recommendation]
            - **Risk Tolerance Considerations**: [How risk appetite affects decision]
            
            #### Optimization Opportunities
            - **Parameter Optimization**: [Variables to fine-tune for better outcomes]
            - **Risk Reduction Priorities**: [Most important risk mitigation actions]
            - **Value Enhancement**: [Opportunities to improve expected outcomes]
            
            ### Implementation Guidance
            #### Monitoring and Control
            - **Key Metrics to Track**: [Most important leading indicators]
            - **Alert Thresholds**: [When to take corrective action]
            - **Review Frequency**: [How often to reassess projections]
            
            #### Adaptive Management
            - **Course Correction Triggers**: [Signals to modify approach]
            - **Flexibility Requirements**: [Where agility is most important]
            - **Learning and Adjustment**: [How to improve predictions over time]
            
            ## Technical Appendix
            
            ### Model Validation
            #### Validation Methods
            - **Historical Back-testing**: [How model was tested against past data]
            - **Cross-validation**: [Statistical validation techniques used]
            - **Expert Review**: [Subject matter expert validation]
            
            #### Model Limitations
            - **Assumption Dependencies**: [Critical assumptions that may not hold]
            - **Data Quality Constraints**: [Limitations in input data]
            - **Model Scope Boundaries**: [What the model does/doesn't cover]
            
            ### Simulation Code and Parameters
            #### Key Model Parameters
            ```python
            # Example parameter configuration
            simulation_parameters = {
                'iterations': 1000,
                'base_outcome': 100,
                'volatility': 0.2,
                'growth_rate': 0.05,
                'risk_factors': [0.1, 0.15, 0.08]
            }
            ```
            
            This comprehensive simulation analysis provides quantitative foundation for strategic decision-making with statistical confidence intervals and risk assessment.
            
            ## What Do These Results Mean? - Simple Explanation for Decision Makers
            
            ### Understanding Monte Carlo Simulation in Plain English
            
            Think of Monte Carlo simulation like this: **Imagine we could look into 1,000 different possible futures for your project and see what happens in each one.** Some futures are great, some are terrible, and most are somewhere in between. This simulation helps us understand:
            
            - **What's most likely to happen?** (The average outcome)
            - **What's the best we can reasonably hope for?** (The optimistic scenario)
            - **What's the worst we should prepare for?** (The pessimistic scenario)
            - **How risky is this decision?** (How much the outcomes vary)
            
            ### Breaking Down the Numbers - What They Really Mean
            
            #### The Three Main Scenarios Explained
            
            **🟢 Optimistic Scenario (90th Percentile)**
            **What it means**: This is like the "best case scenario" - only 1 out of 10 times would things go better than this.
            
            **In simple terms**: 
            - Think of this as your "stretch goal" - it's achievable but requires things to go well
            - This represents the outcome when most factors work in your favor
            - You have a 10% chance of doing even better than this
            - **Real-world analogy**: Like planning a road trip where you hit all green lights and have no traffic
            
            **🟡 Baseline Scenario (50th Percentile - The Middle Ground)**
            **What it means**: This is the "most likely" outcome - half the time you'll do better, half the time worse.
            
            **In simple terms**:
            - This is your "realistic expectation" - what you should probably plan for
            - This represents normal conditions with typical challenges and successes
            - It's like flipping a coin - 50/50 chance of doing better or worse than this
            - **Real-world analogy**: Like your normal commute to work - some days better, some worse, but this is typical
            
            **🔴 Pessimistic Scenario (10th Percentile - Worst Case Planning)**
            **What it means**: This is the "what if things go wrong" scenario - only 1 out of 10 times would things be worse than this.
            
            **In simple terms**:
            - This is your "contingency planning" number - what to prepare for if problems arise
            - You have a 90% chance of doing better than this outcome
            - This helps you understand the downside risk you're accepting
            - **Real-world analogy**: Like planning a road trip accounting for bad weather, traffic jams, and car trouble
            
            #### Key Risk Indicators - What to Watch For
            
            **📊 Standard Deviation (Volatility)**
            - **What it measures**: How much the outcomes vary from the average
            - **High number means**: More unpredictable, higher risk/reward
            - **Low number means**: More predictable, lower risk/reward
            - **Think of it like**: Weather forecast reliability - low volatility is like predicting tomorrow's weather, high volatility is like predicting weather 2 weeks out
            
            **📉 Value at Risk (VaR)**
            - **What it measures**: The maximum loss you might face in bad scenarios
            - **How to read it**: "There's only a 5% chance we'll lose more than [VaR amount]"
            - **Think of it like**: Insurance planning - this tells you the worst-case scenario to prepare for
            
            **📈 Probability of Success**
            - **What it measures**: The chance of meeting or exceeding your targets
            - **How to interpret**: Higher percentage = better odds of success
            - **Think of it like**: Weather forecast - 80% chance of success is like "80% chance of sunny weather"
            
            ### Making Decisions Based on These Results
            
            #### If You're Risk-Averse (Conservative Approach)
            - **Focus on**: The pessimistic scenario numbers
            - **Ask yourself**: "Can we handle the worst-case outcome?"
            - **Decision rule**: Only proceed if the pessimistic scenario is still acceptable
            - **Strategy**: Build extra safety margins and contingency plans
            
            #### If You're Risk-Neutral (Balanced Approach)
            - **Focus on**: The baseline scenario numbers
            - **Ask yourself**: "Is the most likely outcome worth the effort and investment?"
            - **Decision rule**: Proceed if the baseline scenario meets your goals
            - **Strategy**: Plan for the baseline but prepare for deviations
            
            #### If You're Risk-Seeking (Aggressive Approach)
            - **Focus on**: The optimistic scenario potential
            - **Ask yourself**: "What's the upside potential if things go well?"
            - **Decision rule**: Accept higher risk for higher potential rewards
            - **Strategy**: Maximize upside while having contingency plans for downside
            
            ### Red Flags - When to Be Concerned
            
            🚩 **High Volatility Warning**: If the difference between optimistic and pessimistic scenarios is huge, you're looking at a high-risk situation
            
            🚩 **Negative Baseline**: If even the "most likely" scenario doesn't meet your minimum requirements, reconsider the project
            
            🚩 **Low Success Probability**: If the chance of meeting your targets is less than 60-70%, you might need a better strategy
            
            🚩 **Unacceptable Worst Case**: If the pessimistic scenario would be catastrophic for your organization, you need more safeguards
            
            ### Green Lights - Positive Indicators
            
            ✅ **Consistent Positive Outcomes**: All three scenarios (optimistic, baseline, pessimistic) are positive
            
            ✅ **High Success Probability**: 70%+ chance of meeting your key objectives
            
            ✅ **Manageable Downside**: Even the worst-case scenario is survivable and recoverable
            
            ✅ **Good Risk/Reward Ratio**: The potential upside justifies the downside risk
            
            ### Bottom Line Recommendations
            
            **For Executive Summary**:
            Based on running 1,000 different scenarios, here's what the numbers tell us:
            
            1. **Most Likely Outcome**: [Insert baseline scenario result and what it means]
            2. **Best Case Potential**: [Insert optimistic scenario and probability]
            3. **Worst Case Planning**: [Insert pessimistic scenario and probability]
            4. **Overall Risk Level**: [High/Medium/Low based on volatility]
            5. **Recommendation**: [Go/No-Go/Modify based on risk tolerance]
            
            **The simulation essentially answers**: "If we ran this project 1,000 times, here's what would typically happen, what could go right, and what could go wrong - helping you make an informed decision about whether the potential rewards are worth the risks."
            
            ---
            
            *This Monte Carlo simulation analysis transforms complex statistical data into actionable business intelligence, enabling confident strategic decision-making even in uncertain environments.*""",
            markdown=True,
            agent = SimulateAgent.create_agent(),
            output_file="monte_carlo_simulation_analysis_report.md"
        )
            