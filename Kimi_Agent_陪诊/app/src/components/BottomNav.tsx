import { Home, ClipboardList, User } from 'lucide-react';
import { motion } from 'framer-motion';

interface BottomNavProps {
  currentPage: string;
  onPageChange: (page: string) => void;
}

export function BottomNav({ currentPage, onPageChange }: BottomNavProps) {
  const navItems = [
    { id: 'home', label: '首页', icon: Home },
    { id: 'orders', label: '订单', icon: ClipboardList },
    { id: 'profile', label: '我的', icon: User },
  ];

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-100 pb-safe z-50">
      <div className="flex items-center justify-around h-[60px] max-w-md mx-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentPage === item.id;
          
          return (
            <motion.button
              key={item.id}
              onClick={() => onPageChange(item.id)}
              className={`flex flex-col items-center justify-center flex-1 h-full relative ${
                isActive ? 'text-[#3EAF9F]' : 'text-gray-400'
              }`}
              whileTap={{ scale: 0.95 }}
            >
              {isActive && (
                <motion.div
                  layoutId="activeTab"
                  className="absolute top-0 w-8 h-0.5 bg-[#3EAF9F] rounded-full"
                  transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                />
              )}
              <Icon size={22} strokeWidth={isActive ? 2.5 : 2} />
              <span className="text-[11px] mt-1 font-medium">{item.label}</span>
            </motion.button>
          );
        })}
      </div>
    </nav>
  );
}
