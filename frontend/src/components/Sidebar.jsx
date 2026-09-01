import React from 'react';
import { 
  BarChart3, 
  ShieldAlert, 
  Inbox, 
  Receipt, 
  Settings, 
  ExternalLink, 
  HelpCircle, 
  ChevronRight,
  ShieldCheck
} from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab, pendingReviewCount = 2 }) {
  const menuItems = [
    { id: 'overview', label: 'Overview', icon: BarChart3 },
    { id: 'simulator', label: 'Risk Inspector', icon: ShieldAlert },
    { id: 'review', label: 'Review Queue', icon: Inbox, count: pendingReviewCount },
    { id: 'orders', label: 'Orders Ledger', icon: Receipt },
  ];

  return (
    <aside style={{
      width: '240px',
      background: '#0C2340',
      color: '#FFFFFF',
      display: 'flex',
      flexDirection: 'column',
      borderRight: '1px solid #1E3A5F',
      height: '100vh',
      position: 'sticky',
      top: 0,
      flexShrink: 0,
    }}>
      {/* Brand Header */}
      <div style={{
        padding: '1.25rem 1.25rem 1rem',
        borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
          <div style={{
            width: '32px',
            height: '32px',
            borderRadius: '6px',
            background: '#3395FF',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#FFFFFF',
          }}>
            <ShieldCheck size={20} />
          </div>
          <div>
            <div style={{ fontSize: '0.95rem', fontWeight: 700, letterSpacing: '-0.02em' }}>
              Razorpay <span style={{ color: '#3395FF', fontWeight: 500 }}>ReturnGuard</span>
            </div>
            <div style={{ fontSize: '0.72rem', color: '#94A3B8' }}>
              Risk Operations
            </div>
          </div>
        </div>

        {/* Merchant Account Pill */}
        <div style={{
          marginTop: '0.85rem',
          padding: '0.45rem 0.65rem',
          background: 'rgba(255, 255, 255, 0.06)',
          borderRadius: '4px',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          fontSize: '0.75rem',
        }}>
          <div style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            <span style={{ color: '#E2E8F0', fontWeight: 600 }}>D2C Retail Store</span>
            <div style={{ color: '#94A3B8', fontSize: '0.68rem' }}>MID: 894120</div>
          </div>
          <span style={{
            fontSize: '0.65rem',
            fontWeight: 700,
            background: '#10B981',
            color: '#FFFFFF',
            padding: '1px 5px',
            borderRadius: '3px',
          }}>
            LIVE
          </span>
        </div>
      </div>

      {/* Navigation Menu Items */}
      <nav style={{ padding: '1rem 0.75rem', display: 'flex', flexDirection: 'column', gap: '0.25rem', flex: 1 }}>
        <div style={{
          fontSize: '0.68rem',
          fontWeight: 600,
          color: '#64748B',
          textTransform: 'uppercase',
          letterSpacing: '0.05em',
          padding: '0 0.5rem 0.5rem',
        }}>
          Risk Intelligence
        </div>

        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '0.6rem 0.75rem',
                borderRadius: '4px',
                border: 'none',
                background: isActive ? 'rgba(51, 149, 255, 0.15)' : 'transparent',
                color: isActive ? '#38BDF8' : '#CBD5E1',
                fontSize: '0.84rem',
                fontWeight: isActive ? 600 : 500,
                cursor: 'pointer',
                textAlign: 'left',
                transition: 'all 0.15s ease',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
                <Icon size={16} color={isActive ? '#38BDF8' : '#94A3B8'} />
                <span>{item.label}</span>
              </div>
              {item.count && (
                <span style={{
                  background: '#EF4444',
                  color: '#FFFFFF',
                  fontSize: '0.68rem',
                  fontWeight: 700,
                  padding: '1px 6px',
                  borderRadius: '10px',
                }}>
                  {item.count}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Bottom Footer Section */}
      <div style={{
        padding: '1rem',
        borderTop: '1px solid rgba(255, 255, 255, 0.08)',
        fontSize: '0.75rem',
        color: '#94A3B8',
        display: 'flex',
        flexDirection: 'column',
        gap: '0.5rem',
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>Inference SLA:</span>
          <strong style={{ color: '#10B981' }}>0.002 ms</strong>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>Opt. Cutoff:</span>
          <strong style={{ color: '#38BDF8' }}>τ* = 0.20</strong>
        </div>
        <div style={{ borderTop: '1px solid rgba(255, 255, 255, 0.08)', paddingTop: '0.5rem', fontSize: '0.72rem', color: '#64748B' }}>
          Razorpay Buildathon 2026
        </div>
      </div>
    </aside>
  );
}
