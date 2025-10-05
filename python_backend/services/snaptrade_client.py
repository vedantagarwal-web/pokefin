"""
SnapTrade Client - Professional brokerage integration
Handles user registration, connections, and portfolio data fetching
"""

import os
import uuid
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Try to import SnapTrade SDK
try:
    import snaptrade_client as snaptrade
    SNAPTRADE_AVAILABLE = True
except ImportError:
    SNAPTRADE_AVAILABLE = False
    print("⚠️ SnapTrade SDK not available. Using mock data.")

load_dotenv()

class SnapTradeClient:
    """SnapTrade client for brokerage integration"""
    
    def __init__(self):
        self.client_id = os.getenv("SNAPTRADE_CLIENT_ID")
        self.consumer_key = os.getenv("SNAPTRADE_CONSUMER_KEY")
        
        if not self.client_id or not self.consumer_key:
            print("⚠️ SnapTrade credentials not found. Using mock data.")
            self.client = None
            return
        
        # Initialize SnapTrade client
        if not SNAPTRADE_AVAILABLE:
            print("⚠️ SnapTrade SDK not available. Using mock data.")
            self.client = None
            return
            
        try:
            # Initialize with both client_id and consumer_key as per official docs
            self.client = snaptrade.SnapTrade(
                consumer_key=self.consumer_key,
                client_id=self.client_id
            )
            
            # Store credentials for API calls
            self._client_id = self.client_id
            self._consumer_key = self.consumer_key
            
            print("✅ SnapTrade client initialized")
        except Exception as e:
            print(f"❌ SnapTrade client initialization failed: {e}")
            self.client = None
    
    async def create_user(self, user_id: str) -> Dict[str, Any]:
        """Create a new SnapTrade user"""
        if not self.client:
            return {
                "userId": user_id,
                "userSecret": f"mock_secret_{uuid.uuid4().hex[:16]}",
                "mock": True
            }
        
        try:
            # Register user - use simple body format as per official docs
            response = self.client.authentication.register_snap_trade_user(
                body={"userId": user_id}
            )
            return {
                "userId": response.body["userId"],
                "userSecret": response.body["userSecret"],
                "mock": False
            }
        except Exception as e:
            print(f"❌ Error creating SnapTrade user: {e}")
            return {
                "userId": user_id,
                "userSecret": f"mock_secret_{uuid.uuid4().hex[:16]}",
                "mock": True,
                "error": str(e)
            }
    
    async def get_connection_portal_url(self, user_id: str, user_secret: str, redirect_uri: str) -> Dict[str, Any]:
        """Generate connection portal URL for brokerage linking"""
        if not self.client:
            # Return a demo URL that explains the situation
            return {
                "redirect_url": f"https://app.snaptrade.com/demo?user_id={user_id}&message=SnapTrade credentials not configured",
                "mock": True,
                "message": "SnapTrade SDK not available or credentials not configured. Using demo mode.",
                "instructions": [
                    "1. Register at https://snaptrade.com/register",
                    "2. Get your SNAPTRADE_CLIENT_ID and SNAPTRADE_CONSUMER_KEY",
                    "3. Add them to your .env file",
                    "4. Restart the backend server"
                ]
            }
        
        try:
            # Generate connection portal URL with proper parameters
            response = self.client.authentication.login_snap_trade_user(
                custom_redirect=redirect_uri,
                query_params={"userId": user_id, "userSecret": user_secret}
            )
            return {
                "redirect_url": response.body["redirectURI"],
                "mock": False
            }
        except Exception as e:
            print(f"❌ Error generating connection URL: {e}")
            # Check if it's a credentials issue
            if "invalid" in str(e).lower() or "unauthorized" in str(e).lower():
                return {
                    "redirect_url": f"https://app.snaptrade.com/demo?user_id={user_id}&error=invalid_credentials",
                    "mock": True,
                    "error": "Invalid SnapTrade credentials. Please check your SNAPTRADE_CLIENT_ID and SNAPTRADE_CONSUMER_KEY.",
                    "credentials_issue": True
                }
            else:
                # Fallback to direct SnapTrade portal with our credentials
                fallback_url = f"https://app.snaptrade.com/connect?client_id={self.client_id}&user_id={user_id}&redirect_uri={redirect_uri}"
                return {
                    "redirect_url": fallback_url,
                    "mock": False,
                    "fallback": True,
                    "error": str(e)
                }
    
    async def get_user_accounts(self, user_id: str, user_secret: str) -> List[Dict[str, Any]]:
        """Get user's connected accounts"""
        if not self.client:
            return self._get_mock_accounts()
        
        try:
            # First, try to refresh the connection to sync accounts
            try:
                print(f"🔄 Refreshing SnapTrade connection for user {user_id}")
                # Try different refresh methods based on SnapTrade docs
                try:
                    refresh_result = self.client.account_information.refresh_holdings(
                        user_id=user_id,
                        user_secret=user_secret
                    )
                except AttributeError:
                    try:
                        refresh_result = self.client.holdings.refresh_holdings(
                            user_id=user_id,
                            user_secret=user_secret
                        )
                    except AttributeError:
                        # If no refresh method exists, skip it
                        print("ℹ️ No refresh method available, proceeding without refresh")
                        refresh_result = None
                print(f"✅ SnapTrade refresh completed: {refresh_result}")
            except Exception as refresh_error:
                print(f"⚠️ SnapTrade refresh failed (continuing anyway): {refresh_error}")
            
            # Now get the accounts
            print(f"🔍 Calling SnapTrade API: list_user_accounts for user {user_id}")
            accounts = self.client.account_information.list_user_accounts(
                user_id=user_id,
                user_secret=user_secret
            )
            
            print(f"🔍 Raw SnapTrade response type: {type(accounts)}")
            print(f"🔍 Raw SnapTrade response: {accounts}")
            
            # Handle the API response properly
            if hasattr(accounts, 'body'):
                accounts_data = accounts.body
                print(f"🔍 Using accounts.body: {accounts_data}")
            else:
                accounts_data = accounts
                print(f"🔍 Using accounts directly: {accounts_data}")
                
            # Convert to list if it's not already
            if not isinstance(accounts_data, list):
                accounts_data = [accounts_data] if accounts_data else []
                print(f"🔍 Converted to list: {accounts_data}")
                
            print(f"📊 SnapTrade returned {len(accounts_data)} accounts")
            
            return [
                {
                    "id": account.get("id", account.id if hasattr(account, 'id') else str(uuid.uuid4())),
                    "name": account.get("name", account.name if hasattr(account, 'name') else "Account"),
                    "type": account.get("type", account.type if hasattr(account, 'type') else "investment"),
                    "broker": account.get("broker", account.broker if hasattr(account, 'broker') else "Unknown"),
                    "number": account.get("number", account.number if hasattr(account, 'number') else "****")
                }
                for account in accounts_data
            ]
        except Exception as e:
            print(f"❌ Error getting user accounts: {e}")
            print(f"❌ Error type: {type(e)}")
            import traceback
            print(f"❌ Full traceback: {traceback.format_exc()}")
            return self._get_mock_accounts()
    
    async def get_account_positions(self, user_id: str, user_secret: str, account_id: str) -> List[Dict[str, Any]]:
        """Get positions for a specific account"""
        if not self.client:
            return self._get_mock_positions()
        
        try:
            positions = self.client.account_information.get_user_account_positions(
                user_id=user_id,
                user_secret=user_secret,
                account_id=account_id
            )
            
            # Handle the API response properly
            if hasattr(positions, 'body'):
                positions_data = positions.body
            else:
                positions_data = positions
            
            return [
                {
                    "symbol": pos.get("symbol", {}).get("symbol") if isinstance(pos, dict) else pos.symbol.symbol if hasattr(pos, 'symbol') else "Unknown",
                    "name": pos.get("symbol", {}).get("description") if isinstance(pos, dict) else pos.symbol.description if hasattr(pos, 'symbol') else "Unknown",
                    "shares": pos.get("units") if isinstance(pos, dict) else pos.units if hasattr(pos, 'units') else 0,
                    "current_price": pos.get("price") if isinstance(pos, dict) else pos.price if hasattr(pos, 'price') else 0,
                    "market_value": pos.get("market_value") if isinstance(pos, dict) else pos.market_value if hasattr(pos, 'market_value') else 0,
                    "cost_basis": pos.get("cost_basis") if isinstance(pos, dict) else pos.cost_basis if hasattr(pos, 'cost_basis') else 0,
                    "unrealized_pl": pos.get("unrealized_pl") if isinstance(pos, dict) else pos.unrealized_pl if hasattr(pos, 'unrealized_pl') else 0,
                    "unrealized_pl_percent": pos.get("unrealized_pl_percent") if isinstance(pos, dict) else pos.unrealized_pl_percent if hasattr(pos, 'unrealized_pl_percent') else 0
                }
                for pos in positions_data
            ]
        except Exception as e:
            print(f"❌ Error getting account positions: {e}")
            return self._get_mock_positions()
    
    async def get_account_balances(self, user_id: str, user_secret: str, account_id: str) -> Dict[str, Any]:
        """Get account balances"""
        if not self.client:
            return self._get_mock_balances()
        
        try:
            balances = self.client.account_information.get_user_account_balance(
                user_id=user_id,
                user_secret=user_secret,
                account_id=account_id
            )
            
            # Handle the API response properly
            if hasattr(balances, 'body'):
                balances_data = balances.body
            else:
                balances_data = balances
                
            return {
                "cash": balances_data.get("cash") if isinstance(balances_data, dict) else balances_data.cash if hasattr(balances_data, 'cash') else 0,
                "buying_power": balances_data.get("buying_power") if isinstance(balances_data, dict) else balances_data.buying_power if hasattr(balances_data, 'buying_power') else 0,
                "total_equity": balances_data.get("total_equity") if isinstance(balances_data, dict) else balances_data.total_equity if hasattr(balances_data, 'total_equity') else 0,
                "total_equity_previous_close": balances_data.get("total_equity_previous_close") if isinstance(balances_data, dict) else balances_data.total_equity_previous_close if hasattr(balances_data, 'total_equity_previous_close') else 0
            }
        except Exception as e:
            print(f"❌ Error getting account balances: {e}")
            return self._get_mock_balances()
    
    def _get_mock_accounts(self) -> List[Dict[str, Any]]:
        """Return mock account data for testing"""
        return [
            {
                "id": "mock_account_1",
                "name": "Robinhood Account",
                "type": "investment",
                "broker": "Robinhood",
                "number": "****1234"
            }
        ]
    
    def _get_mock_positions(self) -> List[Dict[str, Any]]:
        """Return mock position data for testing"""
        return [
            {
                "symbol": "TSLA",
                "name": "Tesla Inc",
                "shares": 10,
                "current_price": 180.50,
                "market_value": 1805.00,
                "cost_basis": 2000.00,
                "unrealized_pl": -195.00,
                "unrealized_pl_percent": -9.75
            },
            {
                "symbol": "AAPL",
                "name": "Apple Inc",
                "shares": 5,
                "current_price": 175.25,
                "market_value": 876.25,
                "cost_basis": 850.00,
                "unrealized_pl": 26.25,
                "unrealized_pl_percent": 3.09
            },
            {
                "symbol": "VTI",
                "name": "Vanguard Total Stock Market ETF",
                "shares": 25,
                "current_price": 245.80,
                "market_value": 6145.00,
                "cost_basis": 6000.00,
                "unrealized_pl": 145.00,
                "unrealized_pl_percent": 2.42
            }
        ]
    
    def _get_mock_balances(self) -> Dict[str, Any]:
        """Return mock balance data for testing"""
        return {
            "cash": 2500.00,
            "buying_power": 5000.00,
            "total_equity": 8826.25,
            "total_equity_previous_close": 8750.00
        }
    
    async def get_account_transactions(self, user_id: str, user_secret: str, account_id: str) -> List[Dict[str, Any]]:
        """Get transaction history for a specific account"""
        if not self.client:
            return self._get_mock_transactions()
        
        try:
            # Use the activities endpoint for transaction history
            transactions = self.client.transactions_and_reporting.get_activities(
                user_id=user_id,
                user_secret=user_secret,
                account_id=account_id
            )
            
            # Handle the API response properly
            if hasattr(transactions, 'body'):
                transactions_data = transactions.body
            else:
                transactions_data = transactions
            
            return [
                {
                    "id": txn.get("id") if isinstance(txn, dict) else txn.id if hasattr(txn, 'id') else str(uuid.uuid4()),
                    "symbol": txn.get("symbol", {}).get("symbol") if isinstance(txn, dict) else (txn.symbol.symbol if hasattr(txn, 'symbol') and txn.symbol else None),
                    "action": txn.get("action") if isinstance(txn, dict) else txn.action if hasattr(txn, 'action') else "Unknown",
                    "quantity": txn.get("quantity") if isinstance(txn, dict) else txn.quantity if hasattr(txn, 'quantity') else 0,
                    "price": txn.get("price") if isinstance(txn, dict) else txn.price if hasattr(txn, 'price') else 0,
                    "amount": txn.get("amount") if isinstance(txn, dict) else txn.amount if hasattr(txn, 'amount') else 0,
                    "date": txn.get("date") if isinstance(txn, dict) else txn.date if hasattr(txn, 'date') else None,
                    "status": txn.get("status") if isinstance(txn, dict) else txn.status if hasattr(txn, 'status') else "Unknown"
                }
                for txn in transactions_data
            ]
        except Exception as e:
            print(f"❌ Error getting account transactions: {e}")
            return self._get_mock_transactions()
    
    async def get_portfolio_summary(self, user_id: str, user_secret: str) -> Dict[str, Any]:
        """Get comprehensive portfolio summary across all accounts"""
        if not self.client:
            return self._get_mock_portfolio_summary()
        
        try:
            # Get all accounts
            accounts = await self.get_user_accounts(user_id, user_secret)
            
            total_portfolio = {
                "total_equity": 0,
                "total_cash": 0,
                "total_buying_power": 0,
                "day_change": 0,
                "day_change_percent": 0,
                "positions": [],
                "accounts": []
            }
            
            for account in accounts:
                account_id = account["id"]
                
                # Get positions and balances for this account
                positions = await self.get_account_positions(user_id, user_secret, account_id)
                balances = await self.get_account_balances(user_id, user_secret, account_id)
                
                # Add account info
                account_summary = {
                    "id": account_id,
                    "name": account["name"],
                    "broker": account["broker"],
                    "balances": balances,
                    "positions": positions,
                    "position_count": len(positions)
                }
                
                total_portfolio["accounts"].append(account_summary)
                total_portfolio["positions"].extend(positions)
                
                # Aggregate totals
                total_portfolio["total_equity"] += balances.get("total_equity", 0)
                total_portfolio["total_cash"] += balances.get("cash", 0)
                total_portfolio["total_buying_power"] += balances.get("buying_power", 0)
            
            return total_portfolio
            
        except Exception as e:
            print(f"❌ Error getting portfolio summary: {e}")
            return self._get_mock_portfolio_summary()
    
    def _get_mock_transactions(self) -> List[Dict[str, Any]]:
        """Return mock transaction data for testing"""
        return [
            {
                "id": "txn_001",
                "symbol": "TSLA",
                "action": "BUY",
                "quantity": 10,
                "price": 200.00,
                "amount": 2000.00,
                "date": "2024-01-15",
                "status": "COMPLETED"
            },
            {
                "id": "txn_002",
                "symbol": "AAPL",
                "action": "BUY",
                "quantity": 5,
                "price": 170.00,
                "amount": 850.00,
                "date": "2024-01-20",
                "status": "COMPLETED"
            },
            {
                "id": "txn_003",
                "symbol": "VTI",
                "action": "BUY",
                "quantity": 25,
                "price": 240.00,
                "amount": 6000.00,
                "date": "2024-02-01",
                "status": "COMPLETED"
            },
            {
                "id": "txn_004",
                "symbol": "AAPL",
                "action": "DIVIDEND",
                "quantity": 0,
                "price": 0.24,
                "amount": 1.20,
                "date": "2024-02-15",
                "status": "COMPLETED"
            }
        ]
    
    def _get_mock_portfolio_summary(self) -> Dict[str, Any]:
        """Return mock portfolio summary for testing"""
        return {
            "total_equity": 8826.25,
            "total_cash": 2500.00,
            "total_buying_power": 5000.00,
            "day_change": 76.25,
            "day_change_percent": 0.87,
            "positions": [
                {
                    "symbol": "TSLA",
                    "name": "Tesla Inc",
                    "shares": 10,
                    "current_price": 180.50,
                    "market_value": 1805.00,
                    "cost_basis": 2000.00,
                    "unrealized_pl": -195.00,
                    "unrealized_pl_percent": -9.75
                },
                {
                    "symbol": "AAPL",
                    "name": "Apple Inc",
                    "shares": 5,
                    "current_price": 175.25,
                    "market_value": 876.25,
                    "cost_basis": 850.00,
                    "unrealized_pl": 26.25,
                    "unrealized_pl_percent": 3.09
                },
                {
                    "symbol": "VTI",
                    "name": "Vanguard Total Stock Market ETF",
                    "shares": 25,
                    "current_price": 245.80,
                    "market_value": 6145.00,
                    "cost_basis": 6000.00,
                    "unrealized_pl": 145.00,
                    "unrealized_pl_percent": 2.42
                }
            ],
            "accounts": [
                {
                    "id": "mock_account_1",
                    "name": "Robinhood Account",
                    "broker": "Robinhood",
                    "balances": {
                        "cash": 2500.00,
                        "buying_power": 5000.00,
                        "total_equity": 8826.25,
                        "total_equity_previous_close": 8750.00
                    },
                    "positions": [
                        {
                            "symbol": "TSLA",
                            "name": "Tesla Inc",
                            "shares": 10,
                            "current_price": 180.50,
                            "market_value": 1805.00,
                            "cost_basis": 2000.00,
                            "unrealized_pl": -195.00,
                            "unrealized_pl_percent": -9.75
                        },
                        {
                            "symbol": "AAPL",
                            "name": "Apple Inc",
                            "shares": 5,
                            "current_price": 175.25,
                            "market_value": 876.25,
                            "cost_basis": 850.00,
                            "unrealized_pl": 26.25,
                            "unrealized_pl_percent": 3.09
                        },
                        {
                            "symbol": "VTI",
                            "name": "Vanguard Total Stock Market ETF",
                            "shares": 25,
                            "current_price": 245.80,
                            "market_value": 6145.00,
                            "cost_basis": 6000.00,
                            "unrealized_pl": 145.00,
                            "unrealized_pl_percent": 2.42
                        }
                    ],
                    "position_count": 3
                }
            ]
        }

    async def list_connections(self, user_id: str, user_secret: str) -> List[Dict[str, Any]]:
        """List all SnapTrade connections for a user"""
        try:
            if not self.client:
                return self._mock_connections()
            
            print(f"Listing connections for user {user_id}")
            
            # Use the connections API to list connections
            connections = self.client.connections.list_brokerage_authorizations(
                user_id=user_id,
                user_secret=user_secret
            )
            
            if hasattr(connections, 'body'):
                connections_data = connections.body
            else:
                connections_data = connections
                
            return [
                {
                    "authorization_id": conn.get("authorizationId") if isinstance(conn, dict) else conn.authorizationId if hasattr(conn, 'authorizationId') else str(uuid.uuid4()),
                    "broker": conn.get("broker") if isinstance(conn, dict) else conn.broker if hasattr(conn, 'broker') else "Unknown",
                    "status": conn.get("status") if isinstance(conn, dict) else conn.status if hasattr(conn, 'status') else "Unknown",
                    "created_at": conn.get("createdAt") if isinstance(conn, dict) else conn.createdAt if hasattr(conn, 'createdAt') else None
                }
                for conn in connections_data
            ]
            
        except Exception as e:
            print(f"Error listing connections: {e}")
            return self._mock_connections()

    async def delete_connection(self, user_id: str, user_secret: str, authorization_id: str) -> Dict[str, Any]:
        """Delete/disable a SnapTrade connection"""
        try:
            if not self.client:
                return {"success": False, "error": "SnapTrade client not initialized", "mock": True}
            
            print(f"Deleting connection {authorization_id} for user {user_id}")
            
            # Use the connections API to remove the connection
            result = self.client.connections.remove_brokerage_authorization(
                user_id=user_id,
                user_secret=user_secret,
                authorization_id=authorization_id
            )
            
            return {
                "success": True,
                "message": "Connection deleted successfully",
                "authorization_id": authorization_id,
                "mock": False
            }
            
        except Exception as e:
            print(f"Error deleting connection: {e}")
            return {
                "success": False,
                "error": str(e),
                "mock": False
            }

    def _mock_connections(self) -> List[Dict[str, Any]]:
        """Return mock connections data"""
        return [
            {
                "authorization_id": "550e8400-e29b-41d4-a716-446655440001",
                "broker": "Robinhood",
                "status": "active",
                "created_at": "2024-01-01T00:00:00Z"
            },
            {
                "authorization_id": "550e8400-e29b-41d4-a716-446655440002", 
                "broker": "TD Ameritrade",
                "status": "active",
                "created_at": "2024-01-02T00:00:00Z"
            }
        ]
