import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Switch } from './ui/switch';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Shield, Eye, EyeOff, Save, RefreshCw } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api';

const PermissionManager = ({ userId, onPermissionsChange }) => {
  const [permissions, setPermissions] = useState({
    accounts: false,
    transactions: false,
    budgets: false,
    goals: false,
    investments: false,
    debts: false
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // Permission descriptions
  const permissionDescriptions = {
    accounts: {
      title: "Account Balances",
      description: "Access to your account balances and basic account information",
      icon: "💰"
    },
    transactions: {
      title: "Transaction History",
      description: "Access to your income and expense transactions for spending analysis",
      icon: "💳"
    },
    budgets: {
      title: "Budget Information",
      description: "Access to your budget limits, spending, and budget performance",
      icon: "📊"
    },
    goals: {
      title: "Financial Goals",
      description: "Access to your savings goals and progress tracking",
      icon: "🎯"
    },
    investments: {
      title: "Investment Portfolio",
      description: "Access to your investment holdings and portfolio performance",
      icon: "📈"
    },
    debts: {
      title: "Debt Information",
      description: "Access to your loans, credit cards, and debt repayment strategies",
      icon: "💸"
    }
  };

  // Load current permissions
  useEffect(() => {
    loadPermissions();
  }, [userId]);

  const loadPermissions = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`${API_BASE}/permissions/?user_id=${userId}`);
      const data = await response.json();
      
      if (response.ok) {
        setPermissions(data.permissions);
      } else {
        setError(data.error || 'Failed to load permissions');
      }
    } catch (err) {
      setError('Network error while loading permissions');
      console.error('Error loading permissions:', err);
    } finally {
      setLoading(false);
    }
  };

  const savePermissions = async () => {
    try {
      setSaving(true);
      setError(null);
      setSuccess(null);
      
      const response = await fetch(`${API_BASE}/permissions/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          permissions: permissions
        })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setSuccess('Permissions updated successfully!');
        if (onPermissionsChange) {
          onPermissionsChange(permissions);
        }
        // Clear success message after 3 seconds
        setTimeout(() => setSuccess(null), 3000);
      } else {
        setError(data.error || 'Failed to update permissions');
      }
    } catch (err) {
      setError('Network error while saving permissions');
      console.error('Error saving permissions:', err);
    } finally {
      setSaving(false);
    }
  };

  const togglePermission = (permission) => {
    setPermissions(prev => ({
      ...prev,
      [permission]: !prev[permission]
    }));
  };

  const grantAllPermissions = () => {
    const allTrue = Object.keys(permissions).reduce((acc, key) => {
      acc[key] = true;
      return acc;
    }, {});
    setPermissions(allTrue);
  };

  const revokeAllPermissions = () => {
    const allFalse = Object.keys(permissions).reduce((acc, key) => {
      acc[key] = false;
      return acc;
    }, {});
    setPermissions(allFalse);
  };

  const getPermissionCount = () => {
    return Object.values(permissions).filter(Boolean).length;
  };

  if (loading) {
    return (
      <Card className="w-full max-w-4xl mx-auto">
        <CardContent className="p-6">
          <div className="flex items-center justify-center">
            <RefreshCw className="w-6 h-6 animate-spin mr-2" />
            Loading permissions...
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Shield className="w-5 h-5" />
          AI Assistant Data Permissions
        </CardTitle>
        <p className="text-sm text-gray-600">
          Control what data the AI assistant can access to provide personalized insights.
          Your privacy is protected - you can grant or revoke permissions at any time.
        </p>
      </CardHeader>
      
      <CardContent className="space-y-6">
        {/* Status Messages */}
        {error && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}
        
        {success && (
          <div className="p-3 bg-green-50 border border-green-200 rounded-lg text-green-700">
            {success}
          </div>
        )}

        {/* Permission Summary */}
        <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg">
          <div className="flex items-center gap-2">
            <Badge variant={getPermissionCount() > 0 ? "default" : "secondary"}>
              {getPermissionCount()} of {Object.keys(permissions).length} permissions granted
            </Badge>
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={grantAllPermissions}
              disabled={saving}
            >
              <Eye className="w-4 h-4 mr-1" />
              Grant All
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={revokeAllPermissions}
              disabled={saving}
            >
              <EyeOff className="w-4 h-4 mr-1" />
              Revoke All
            </Button>
          </div>
        </div>

        {/* Individual Permissions */}
        <div className="grid gap-4">
          {Object.entries(permissionDescriptions).map(([key, info]) => (
            <div
              key={key}
              className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-start gap-3">
                <div className="text-2xl">{info.icon}</div>
                <div>
                  <h3 className="font-medium text-gray-900">{info.title}</h3>
                  <p className="text-sm text-gray-600">{info.description}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-500">
                  {permissions[key] ? 'Granted' : 'Denied'}
                </span>
                <Switch
                  checked={permissions[key]}
                  onCheckedChange={() => togglePermission(key)}
                  disabled={saving}
                />
              </div>
            </div>
          ))}
        </div>

        {/* Save Button */}
        <div className="flex justify-end pt-4 border-t">
          <Button
            onClick={savePermissions}
            disabled={saving}
            className="min-w-[120px]"
          >
            {saving ? (
              <>
                <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Save className="w-4 h-4 mr-2" />
                Save Permissions
              </>
            )}
          </Button>
        </div>

        {/* Privacy Note */}
        <div className="p-4 bg-gray-50 rounded-lg">
          <h4 className="font-medium text-gray-900 mb-2">🔒 Privacy & Security</h4>
          <ul className="text-sm text-gray-600 space-y-1">
            <li>• Your data is only accessed when you explicitly grant permission</li>
            <li>• You can revoke permissions at any time</li>
            <li>• The AI assistant only uses data you've authorized</li>
            <li>• Your financial data is encrypted and secure</li>
          </ul>
        </div>
      </CardContent>
    </Card>
  );
};

export default PermissionManager;
