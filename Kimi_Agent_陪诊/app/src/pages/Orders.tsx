import { useState } from 'react';
import { motion } from 'framer-motion';
import { ClipboardList, Calendar, MapPin, User, Clock } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

const orders = [
  {
    id: '1',
    type: 'booking',
    status: 'pending',
    statusText: '待服务',
    hospital: '市中心人民医院',
    service: '全程陪诊',
    date: '2024-03-30',
    time: '09:00',
    price: 268,
    patientName: '张大爷',
  },
  {
    id: '2',
    type: 'booking',
    status: 'completed',
    statusText: '已完成',
    hospital: '市第一人民医院',
    service: '普通陪诊',
    date: '2024-03-25',
    time: '14:00',
    price: 128,
    patientName: '李阿姨',
  },
  {
    id: '3',
    type: 'training',
    status: 'processing',
    statusText: '培训中',
    course: '基础培训班',
    startDate: '2024-03-20',
    endDate: '2024-03-27',
    price: 1980,
  },
];

export function Orders() {
  const [activeTab, setActiveTab] = useState('all');

  const filteredOrders = activeTab === 'all' 
    ? orders 
    : orders.filter(o => o.type === activeTab);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'bg-orange-100 text-orange-600';
      case 'processing':
        return 'bg-blue-100 text-blue-600';
      case 'completed':
        return 'bg-green-100 text-green-600';
      default:
        return 'bg-gray-100 text-gray-600';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      {/* Header */}
      <div className="bg-white sticky top-0 z-10 border-b border-gray-100">
        <div className="flex items-center justify-center h-14 px-4">
          <h1 className="text-lg font-semibold">我的订单</h1>
        </div>
      </div>

      {/* Tabs */}
      <div className="px-4 py-4">
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-3 bg-white">
            <TabsTrigger value="all">全部</TabsTrigger>
            <TabsTrigger value="booking">陪诊</TabsTrigger>
            <TabsTrigger value="training">培训</TabsTrigger>
          </TabsList>

          <TabsContent value={activeTab} className="mt-4 space-y-3">
            {filteredOrders.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-16">
                <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                  <ClipboardList size={32} className="text-gray-400" />
                </div>
                <p className="text-gray-500">暂无订单</p>
              </div>
            ) : (
              filteredOrders.map((order, index) => (
                <motion.div
                  key={order.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="bg-white rounded-xl p-4 shadow-sm"
                >
                  {/* Order Header */}
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-gray-400">订单号: {order.id}20240329</span>
                    </div>
                    <Badge className={`${getStatusColor(order.status)} text-xs`}>
                      {order.statusText}
                    </Badge>
                  </div>

                  {/* Order Content */}
                  {order.type === 'booking' ? (
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <MapPin size={14} className="text-gray-400" />
                        <span className="text-sm text-gray-700">{order.hospital}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <User size={14} className="text-gray-400" />
                        <span className="text-sm text-gray-700">{order.service} · {order.patientName}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Calendar size={14} className="text-gray-400" />
                        <span className="text-sm text-gray-700">{order.date} {order.time}</span>
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <ClipboardList size={14} className="text-gray-400" />
                        <span className="text-sm text-gray-700">{order.course}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Clock size={14} className="text-gray-400" />
                        <span className="text-sm text-gray-700">{order.startDate} 至 {order.endDate}</span>
                      </div>
                    </div>
                  )}

                  {/* Order Footer */}
                  <div className="flex items-center justify-between mt-3 pt-3 border-t border-gray-100">
                    <span className="text-sm text-gray-500">
                      合计: <span className="text-[#FF8C42] font-bold">¥{order.price}</span>
                    </span>
                    {order.status === 'pending' && (
                      <button className="px-4 py-1.5 bg-[#3EAF9F] text-white text-sm rounded-lg">
                        联系陪诊师
                      </button>
                    )}
                  </div>
                </motion.div>
              ))
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
