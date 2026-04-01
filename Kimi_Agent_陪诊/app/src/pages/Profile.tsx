import { motion } from 'framer-motion';
import { Phone, MapPin, ChevronRight, Heart, FileText, MessageCircle, Settings, HelpCircle } from 'lucide-react';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';

const menuItems = [
  { icon: Heart, label: '我的收藏', badge: null },
  { icon: FileText, label: '就诊记录', badge: '3' },
  { icon: MessageCircle, label: '在线客服', badge: null },
  { icon: Settings, label: '设置', badge: null },
  { icon: HelpCircle, label: '帮助中心', badge: null },
];

export function Profile() {
  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      {/* Header Background */}
      <div className="bg-[#3EAF9F] h-32 rounded-b-[32px]" />

      {/* Profile Card */}
      <div className="px-4 -mt-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-2xl p-5 shadow-sm"
        >
          <div className="flex items-center gap-4">
            <Avatar className="w-16 h-16 border-4 border-white shadow-md">
              <AvatarImage src="/images/avatar1.jpg" alt="用户头像" />
              <AvatarFallback className="bg-[#E8F6F4] text-[#3EAF9F]">用</AvatarFallback>
            </Avatar>
            <div className="flex-1">
              <h2 className="text-lg font-semibold text-gray-800">张三</h2>
              <div className="flex items-center gap-3 mt-1 text-sm text-gray-500">
                <span className="flex items-center gap-1">
                  <Phone size={12} />
                  138****8888
                </span>
              </div>
              <div className="flex items-center gap-1 mt-1 text-sm text-gray-500">
                <MapPin size={12} />
                北京市朝阳区
              </div>
            </div>
          </div>

          {/* Stats */}
          <div className="flex items-center justify-around mt-5 pt-5 border-t border-gray-100">
            <div className="text-center">
              <p className="text-xl font-bold text-gray-800">5</p>
              <p className="text-xs text-gray-500 mt-0.5">陪诊次数</p>
            </div>
            <div className="w-px h-8 bg-gray-200" />
            <div className="text-center">
              <p className="text-xl font-bold text-gray-800">2</p>
              <p className="text-xs text-gray-500 mt-0.5">收藏医院</p>
            </div>
            <div className="w-px h-8 bg-gray-200" />
            <div className="text-center">
              <p className="text-xl font-bold text-gray-800">1</p>
              <p className="text-xs text-gray-500 mt-0.5">培训课程</p>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Menu */}
      <div className="px-4 mt-4">
        <div className="bg-white rounded-2xl overflow-hidden shadow-sm">
          {menuItems.map((item, index) => {
            const Icon = item.icon;
            return (
              <motion.button
                key={item.label}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                className={`w-full flex items-center justify-between p-4 ${
                  index !== menuItems.length - 1 ? 'border-b border-gray-100' : ''
                }`}
                whileTap={{ scale: 0.99 }}
              >
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 bg-[#E8F6F4] rounded-lg flex items-center justify-center">
                    <Icon size={18} className="text-[#3EAF9F]" />
                  </div>
                  <span className="text-sm text-gray-700">{item.label}</span>
                </div>
                <div className="flex items-center gap-2">
                  {item.badge && (
                    <span className="w-5 h-5 bg-[#FF8C42] text-white text-xs rounded-full flex items-center justify-center">
                      {item.badge}
                    </span>
                  )}
                  <ChevronRight size={16} className="text-gray-400" />
                </div>
              </motion.button>
            );
          })}
        </div>
      </div>

      {/* Version */}
      <div className="text-center mt-8">
        <p className="text-xs text-gray-400">版本号 v1.0.0</p>
      </div>
    </div>
  );
}
