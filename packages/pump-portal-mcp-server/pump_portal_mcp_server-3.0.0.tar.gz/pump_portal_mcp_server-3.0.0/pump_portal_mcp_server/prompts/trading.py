"""
Trading Prompts

MCP prompts for trading operations and strategies.
"""

from fastmcp import FastMCP


def register_trading_prompts(server: FastMCP):
    """Register trading-related prompts with the MCP server."""

    @server.prompt()
    def token_launch_checklist() -> str:
        """
        Checklist for launching a new token.

        This prompt provides a comprehensive checklist for token creators
        to ensure they've covered all important aspects before launch.
        """
        return """# Token Launch Checklist

## Pre-Launch Requirements
- [ ] Token name decided (unique and memorable)
- [ ] Symbol chosen (1-10 characters, ideally 3-5)
- [ ] Token description written (clear and compelling)
- [ ] Token image designed (square format, high quality)
- [ ] Social media accounts created (Twitter, Telegram)
- [ ] Website/landing page prepared
- [ ] Dev buy amount determined (minimum 0.01 SOL)

## Technical Setup
- [ ] Create wallet using create_wallet tool
- [ ] Save private key securely
- [ ] Test API key functionality
- [ ] Configure trading parameters (slippage, priority fees)

## Token Creation Process
1. Use create_token tool with prepared metadata
2. Set appropriate dev buy amount
3. Include social links and website
4. Upload high-quality token image
5. Review transaction details on Solscan

## Post-Launch Strategy
- [ ] Monitor initial trading activity
- [ ] Engage with community on social channels
- [ ] Consider liquidity provision strategy
- [ ] Set up regular fee claiming schedule
- [ ] Track token performance metrics

## Risk Management
- [ ] Understand volatility risks
- [ ] Set realistic expectations
- [ ] Prepare community management plan
- [ ] Monitor for suspicious trading patterns

## Security Considerations
- [ ] Private key stored securely
- [ ] Never share private key or API key
- [ ] Use secure internet connection
- [ ] Enable additional security measures where possible

Remember: Trading involves risk including potential loss of principal. Always do your own research."""

    @server.prompt()
    def trading_strategy_guide() -> str:
        """
        Guide for developing trading strategies.

        This prompt provides guidance on developing and executing
        effective trading strategies on PumpPortal.
        """
        return """# Trading Strategy Guide

## Market Analysis
- Research token fundamentals and team
- Analyze market sentiment and community engagement
- Study historical price patterns and volume
- Monitor social media mentions and news
- Check token distribution and holder analysis

## Entry Strategies
- **Dollar Cost Averaging**: Buy fixed amounts at regular intervals
- **Dip Buying**: Purchase during price corrections
- **Breakout Trading**: Buy when price breaks resistance levels
- **News-Based Trading**: React to positive announcements
- **Community Momentum**: Follow growing community engagement

## Risk Management
- Set stop-loss levels (typically 10-20%)
- Use position sizing (max 5-10% per trade)
- Take profits at predetermined levels
- Avoid emotional trading decisions
- Keep a trading journal

## Technical Indicators
- **Volume**: High volume confirms price movements
- **Slippage Settings**: Adjust based on market conditions
- **Pool Selection**: Choose appropriate DEX for your strategy
- **Priority Fees**: Higher fees for faster execution during high volatility

## Pool Types Guide
- **pump**: New token launches, high volatility
- **raydium**: Established tokens, better liquidity
- **pump-amm**: Automated market maker for pump tokens
- **auto**: Let system select optimal pool

## Exit Strategies
- Set profit targets (2x, 5x, 10x)
- Scale out of positions gradually
- Take partial profits at milestones
- Reassess thesis if fundamentals change
- Don't let winners turn into losers

## Common Mistakes to Avoid
- FOMO buying (Fear Of Missing Out)
- Revenge trading after losses
- Ignoring market trends
- Over-leveraging positions
- Not having a clear exit plan

## Advanced Concepts
- **Liquidity Analysis**: Monitor pool depth and trading volume
- **Holder Distribution**: Watch for whale movements
- **Cross-Platform Analysis**: Compare prices across DEXs
- **Macro Trends**: Consider broader Solana ecosystem trends

Remember: Past performance does not guarantee future results. Always trade within your means."""

    @server.prompt()
    def portfolio_management() -> str:
        """
        Portfolio management for token investments.

        This prompt provides guidance on managing a diversified
        portfolio of token investments.
        """
        return """# Portfolio Management Guide

## Diversification Strategy
- Spread investments across multiple tokens
- Include different risk levels (high/medium/low)
- Consider various sectors and use cases
- Allocate based on risk tolerance and goals
- Rebalance periodically

## Position Sizing
- **High Risk/High Reward**: 1-3% per position
- **Medium Risk**: 3-7% per position
- **Lower Risk**: 7-15% per position
- Keep cash reserves for opportunities
- Never go all-in on one token

## Risk Assessment
- Evaluate team and development progress
- Assess community strength and engagement
- Review token economics and utility
- Consider market conditions and timing
- Monitor competitive landscape

## Performance Tracking
- Maintain detailed trading records
- Track profit/loss for each position
- Monitor portfolio allocation percentages
- Record reasons for entry/exit decisions
- Review performance regularly

## Rebalancing Strategy
- Take profits on outperformers
- Add to undervalued positions
- Cut losses on underperformers
- Maintain target allocation percentages
- Consider tax implications

## Portfolio Types
- **Conservative**: 70% stable tokens, 30% higher risk
- **Balanced**: 50% stable tokens, 50% higher risk
- **Aggressive**: 30% stable tokens, 70% higher risk
- **Speculative**: Mostly high-risk, high-reward tokens

## Monitoring Schedule
- **Daily**: Check price movements and news
- **Weekly**: Review portfolio performance
- **Monthly**: Rebalance if needed
- **Quarterly**: Comprehensive strategy review
- **Annually**: Long-term goal assessment

## Warning Signs
- Sudden price drops without news
- Development team going quiet
- Community engagement declining
- Unusual token movements
- Negative sentiment on social media

## Long-Term Considerations
- Token utility and real-world use cases
- Partnerships and ecosystem integration
- Regulatory developments
- Technology upgrades and improvements
- Overall market cycle position

Remember: Portfolio management is an ongoing process that requires regular attention and adjustment."""