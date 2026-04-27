import { NavLink } from 'react-router-dom';
import { 
  HiOutlineChartBar, HiOutlineCurrencyDollar, HiOutlineUsers, 
  HiOutlineCube, HiOutlineOfficeBuilding, HiOutlineTruck, HiOutlineSpeakerphone 
} from 'react-icons/hi';

const navItems = [
  { path: '/', label: 'Executive', icon: <HiOutlineChartBar /> },
  { path: '/sales', label: 'Sales', icon: <HiOutlineCurrencyDollar /> },
  { path: '/customers', label: 'Customers', icon: <HiOutlineUsers /> },
  { path: '/products', label: 'Products', icon: <HiOutlineCube /> },
  { path: '/stores', label: 'Stores', icon: <HiOutlineOfficeBuilding /> },
  { path: '/operations', label: 'Operations', icon: <HiOutlineTruck /> },
  { path: '/marketing', label: 'Marketing', icon: <HiOutlineSpeakerphone /> },
];

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo">🛒</div>
        <div>
          <div className="sidebar-title">RetailMart AI</div>
          <div className="sidebar-subtitle">Analytics Platform</div>
        </div>
      </div>
      <nav className="sidebar-nav">
        <div className="nav-section-title">Dashboard</div>
        {navItems.map(item => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === '/'}
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            <span className="nav-icon">{item.icon}</span>
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
