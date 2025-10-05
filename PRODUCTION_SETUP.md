# Orthogonal Production Setup Guide

This guide will help you set up Orthogonal for production with Supabase authentication, database, and all necessary configurations.

## 🚀 Quick Start

1. **Install Dependencies**
   ```bash
   cd python_backend
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables**
   Create a `.env` file in the `python_backend` directory with the following variables:

   ```env
   # Supabase Configuration (REQUIRED)
   SUPABASE_URL=https://empxwjsdjszlvbplmtts.supabase.co
   SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVtcHh3anNkanN6bHZicGxtdHRzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk0NTExNTcsImV4cCI6MjA3NTAyNzE1N30.jXNKBJrapzqj2mEM1lhNdiC2ns2OoGvj3k43E9elSUE

   # OpenAI Configuration (REQUIRED)
   OPENAI_API_KEY=your_openai_api_key_here

   # Financial Datasets AI (REQUIRED)
   FINANCIAL_DATASETS_API_KEY=your_financial_datasets_key_here

   # Exa AI (REQUIRED)
   EXA_API_KEY=your_exa_api_key_here

   # SnapTrade Configuration (for brokerage connections)
   SNAPTRADE_CONSUMER_KEY=your_snaptrade_consumer_key_here
   SNAPTRADE_CLIENT_ID=your_snaptrade_client_id_here

   # Robinhood Configuration (legacy)
   ROBINHOOD_CLIENT_ID=your_robinhood_client_id_here

   # Application Configuration
   NODE_ENV=production
   PORT=8787
   PYTHON_PORT=8788

   # Security (REQUIRED for production)
   JWT_SECRET=your_jwt_secret_here
   SESSION_SECRET=your_session_secret_here
   ```

3. **Start the Application**
   ```bash
   ./start-full-system.sh
   ```

## 🏗️ Architecture Overview

### Database Schema (Supabase)
- **profiles**: User profiles and subscription tiers
- **portfolios**: User investment portfolios
- **portfolio_positions**: Individual stock positions
- **trades**: Trade history and transactions
- **brokerage_connections**: Connected brokerage accounts
- **ai_sessions**: Chat/conversation sessions
- **ai_messages**: Individual messages in sessions
- **watchlists**: User watchlists
- **watchlist_items**: Stocks in watchlists

### Authentication Flow
1. User signs up/signs in via Supabase Auth
2. JWT token stored in localStorage
3. All API calls include Bearer token
4. Backend validates token with Supabase
5. Row Level Security (RLS) ensures data isolation

### API Endpoints
- `POST /api/auth/signup` - User registration
- `POST /api/auth/signin` - User login
- `POST /api/auth/signout` - User logout
- `GET /api/auth/user` - Get current user
- `GET /api/user/profile` - Get user profile
- `PUT /api/user/profile` - Update user profile
- `POST /api/portfolios` - Create portfolio
- `GET /api/portfolios` - Get user portfolios

## 🔐 Security Features

### Row Level Security (RLS)
All database tables have RLS enabled with policies that ensure:
- Users can only access their own data
- Public watchlists are accessible to all users
- Proper user isolation for sensitive financial data

### Authentication
- Supabase Auth handles user registration/login
- JWT tokens for API authentication
- Automatic token refresh
- Secure password hashing

### Data Privacy
- User data is completely isolated
- No cross-user data access
- Encrypted connections (HTTPS)
- Secure API key storage

## 📊 Database Features

### Portfolio Management
- Multiple portfolios per user
- Real-time position tracking
- Trade history with fees and notes
- Performance calculations

### AI Session Management
- Persistent chat history
- Session metadata storage
- Tool call tracking
- Message threading

### Watchlist System
- Personal and public watchlists
- Price tracking at addition time
- Notes and annotations
- Symbol management

## 🚀 Production Deployment

### Environment Setup
1. **Supabase Project**: Already configured with database schema
2. **API Keys**: Obtain required API keys for all services
3. **Security**: Generate secure JWT and session secrets
4. **Domain**: Configure custom domain and SSL

### Deployment Checklist
- [ ] All environment variables configured
- [ ] Supabase project active and healthy
- [ ] API keys valid and tested
- [ ] SSL certificate configured
- [ ] Database backups enabled
- [ ] Monitoring and logging setup
- [ ] Error handling tested
- [ ] Performance optimization

### Scaling Considerations
- **Database**: Supabase handles scaling automatically
- **API**: FastAPI with async support for high concurrency
- **Frontend**: Static files can be CDN-hosted
- **Authentication**: Supabase Auth scales automatically

## 🔧 Development vs Production

### Development
- Local Supabase instance (optional)
- Development API keys
- Hot reloading enabled
- Debug logging

### Production
- Production Supabase project
- Production API keys
- Optimized builds
- Error monitoring
- Performance monitoring

## 📈 Monitoring & Analytics

### Key Metrics to Track
- User registration and retention
- Portfolio creation and usage
- AI session engagement
- API response times
- Error rates

### Tools Integration
- Supabase Analytics
- Custom logging in FastAPI
- Frontend error tracking
- Performance monitoring

## 🛠️ Troubleshooting

### Common Issues
1. **Authentication Errors**: Check Supabase credentials
2. **Database Errors**: Verify RLS policies
3. **API Key Issues**: Validate all service keys
4. **CORS Issues**: Check frontend/backend origins

### Debug Mode
Enable debug logging by setting:
```env
DEBUG=true
LOG_LEVEL=debug
```

## 📚 Additional Resources

- [Supabase Documentation](https://supabase.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Financial Datasets AI Documentation](https://financialdatasets.com/docs)

## 🤝 Support

For issues and questions:
1. Check the troubleshooting section
2. Review Supabase project logs
3. Check API service status
4. Contact development team

---

**Note**: This setup provides a production-ready foundation for Orthogonal with enterprise-grade security, scalability, and monitoring capabilities.
