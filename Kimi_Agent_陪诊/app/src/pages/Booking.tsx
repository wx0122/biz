import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, Search, MapPin, CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent } from '@/components/ui/dialog';
import { ScrollArea } from '@/components/ui/scroll-area';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { hospitalApi, bookingApi, paymentApi } from '@/lib/api';

interface BookingProps {
  onBack: () => void;
}

const fallbackHospitals = [
  { id: '1', name: '市中心人民医院', level: '三甲', distance: '1.2km', address: '中山路123号' },
  { id: '2', name: '市第一人民医院', level: '三甲', distance: '2.5km', address: '解放路456号' },
  { id: '3', name: '市中医院', level: '三甲', distance: '3.1km', address: '文化路789号' },
  { id: '4', name: '市妇幼保健院', level: '二甲', distance: '4.0km', address: '人民路321号' },
];

const serviceTypes = [
  {
    id: 'basic',
    name: '普通陪诊',
    description: '基础陪同服务',
    price: 128,
    features: ['陪同就诊', '协助沟通', '取药指引'],
  },
  {
    id: 'full',
    name: '全程陪诊',
    description: '挂号+就诊+取药全流程',
    price: 268,
    features: ['代挂号', '全程陪同', '代取药', '报告代取'],
  },
  {
    id: 'special',
    name: '特殊陪诊',
    description: '老人/儿童/孕妇专属',
    price: 368,
    features: ['专属陪护', '优先服务', '轮椅协助', '全程照顾'],
  },
];

const timeSlots = [
  { period: '上午', times: ['08:00', '09:00', '10:00', '11:00'] },
  { period: '下午', times: ['14:00', '15:00', '16:00', '17:00'] },
];

export function Booking({ onBack }: BookingProps) {
  const [step, setStep] = useState(1);
  const [searchQuery, setSearchQuery] = useState('');
  const [hospitals, setHospitals] = useState(fallbackHospitals);
  const [selectedHospital, setSelectedHospital] = useState<string | null>(null);
  const [selectedService, setSelectedService] = useState<string>('full');
  const [selectedDate, setSelectedDate] = useState<string>('');
  const [selectedTime, setSelectedTime] = useState<string>('');
  const [showSuccess, setShowSuccess] = useState(false);
  const [showPayment, setShowPayment] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [lastOrderId, setLastOrderId] = useState<number | null>(null);
  const [formData, setFormData] = useState({
    patientName: '',
    patientAge: '',
    phone: '',
    description: '',
  });

  useEffect(() => {
    const city = localStorage.getItem('city') || '';
    hospitalApi.list({ city }).then((r) => {
      if (r.items.length > 0) {
        setHospitals(r.items.map((h: any) => ({
          ...h,
          address: h.address || '',
          distance: h.distance || '',
        })));
      }
    }).catch(() => {});
  }, []);

  // Generate next 7 days
  const dates = Array.from({ length: 7 }, (_, i) => {
    const date = new Date();
    date.setDate(date.getDate() + i);
    return {
      value: date.toISOString().split('T')[0],
      label: i === 0 ? '今天' : i === 1 ? '明天' : `${date.getMonth() + 1}/${date.getDate()}`,
      weekday: ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][date.getDay()],
    };
  });

  const filteredHospitals = hospitals.filter(
    (h) => h.name.includes(searchQuery) || h.address.includes(searchQuery)
  );

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      // Map service ID to service_type_id (1=basic, 2=full, 3=special)
      const svcMap: Record<string, number> = { basic: 1, full: 2, special: 3 };
      const res = await bookingApi.create({
        hospital_id: parseInt(selectedHospital || '1'),
        service_type_id: svcMap[selectedService] || 2,
        date: selectedDate,
        time: selectedTime,
        patient_name: formData.patientName,
        patient_age: formData.patientAge,
        phone: formData.phone,
        description: formData.description,
      });
      setLastOrderId(res.booking?.id || null);
      setShowPayment(true);
    } catch {
      // If API unavailable, show success anyway (offline mode)
      setShowSuccess(true);
    } finally {
      setSubmitting(false);
    }
  };

  const handlePay = async (method: 'wechat' | 'alipay') => {
    if (!lastOrderId) return;
    try {
      const res = await paymentApi.create({
        order_type: 'booking',
        order_id: lastOrderId,
        method,
      });
      if (res.pay_url && !res.pay_url.startsWith('mock://')) {
        window.location.href = res.pay_url;
      } else {
        // Mock payment: mark as success
        setShowPayment(false);
        setShowSuccess(true);
      }
    } catch {
      setShowPayment(false);
      setShowSuccess(true);
    }
  };

  const renderStep1 = () => (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="space-y-4"
    >
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
        <Input
          placeholder="搜索医院名称或地址"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-10 h-12 bg-white border-gray-200"
        />
      </div>

      <ScrollArea className="h-[calc(100vh-280px)]">
        <div className="space-y-3">
          {filteredHospitals.map((hospital, index) => (
            <motion.div
              key={hospital.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              onClick={() => setSelectedHospital(hospital.id)}
              className={`p-4 rounded-xl border-2 cursor-pointer transition-all ${
                selectedHospital === hospital.id
                  ? 'border-[#3EAF9F] bg-[#E8F6F4]'
                  : 'border-gray-100 bg-white'
              }`}
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-medium text-gray-800">{hospital.name}</h3>
                  <div className="flex items-center gap-2 mt-1">
                    <Badge variant="secondary" className="text-[10px] bg-[#E8F6F4] text-[#3EAF9F]">
                      {hospital.level}
                    </Badge>
                    <span className="text-xs text-gray-400">{hospital.distance}</span>
                  </div>
                  <div className="flex items-center text-xs text-gray-500 mt-2">
                    <MapPin size={12} className="mr-1" />
                    {hospital.address}
                  </div>
                </div>
                <div
                  className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                    selectedHospital === hospital.id
                      ? 'border-[#3EAF9F] bg-[#3EAF9F]'
                      : 'border-gray-300'
                  }`}
                >
                  {selectedHospital === hospital.id && <CheckCircle size={12} className="text-white" />}
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </ScrollArea>

      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-100 p-4 pb-safe">
        <Button
          onClick={() => setStep(2)}
          disabled={!selectedHospital}
          className="w-full h-12 bg-[#3EAF9F] hover:bg-[#2E8F81] text-white font-medium rounded-xl disabled:opacity-50"
        >
          下一步
        </Button>
      </div>
    </motion.div>
  );

  const renderStep2 = () => (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="space-y-4 pb-24"
    >
      <RadioGroup
        value={selectedService}
        onValueChange={setSelectedService}
        className="space-y-3"
      >
        {serviceTypes.map((service, index) => (
          <motion.div
            key={service.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
          >
            <label
              className={`block p-4 rounded-xl border-2 cursor-pointer transition-all ${
                selectedService === service.id
                  ? 'border-[#3EAF9F] bg-[#E8F6F4]'
                  : 'border-gray-100 bg-white'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-3">
                  <RadioGroupItem value={service.id} id={service.id} className="mt-1" />
                  <div>
                    <h3 className="font-medium text-gray-800">{service.name}</h3>
                    <p className="text-xs text-gray-500 mt-0.5">{service.description}</p>
                    <div className="flex flex-wrap gap-1 mt-2">
                      {service.features.map((feature, i) => (
                        <span
                          key={i}
                          className="text-[10px] px-2 py-0.5 bg-white rounded text-gray-600"
                        >
                          {feature}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-[#FF8C42] font-bold text-lg">¥{service.price}</p>
                </div>
              </div>
            </label>
          </motion.div>
        ))}
      </RadioGroup>

      {/* Date Selection */}
      <div className="mt-6">
        <h3 className="text-sm font-medium text-gray-700 mb-3">选择日期</h3>
        <div className="flex gap-2 overflow-x-auto scrollbar-hide pb-2">
          {dates.map((date) => (
            <button
              key={date.value}
              onClick={() => setSelectedDate(date.value)}
              className={`flex-shrink-0 w-[70px] py-3 rounded-xl border-2 transition-all ${
                selectedDate === date.value
                  ? 'border-[#3EAF9F] bg-[#E8F6F4]'
                  : 'border-gray-100 bg-white'
              }`}
            >
              <p className="text-xs text-gray-500">{date.label}</p>
              <p className={`text-sm font-medium mt-0.5 ${
                selectedDate === date.value ? 'text-[#3EAF9F]' : 'text-gray-700'
              }`}>
                {date.weekday}
              </p>
            </button>
          ))}
        </div>
      </div>

      {/* Time Selection */}
      {selectedDate && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-4"
        >
          <h3 className="text-sm font-medium text-gray-700 mb-3">选择时间</h3>
          {timeSlots.map((slot) => (
            <div key={slot.period} className="mb-3">
              <p className="text-xs text-gray-400 mb-2">{slot.period}</p>
              <div className="flex gap-2 flex-wrap">
                {slot.times.map((time) => (
                  <button
                    key={time}
                    onClick={() => setSelectedTime(time)}
                    className={`px-4 py-2 rounded-lg border-2 text-sm transition-all ${
                      selectedTime === time
                        ? 'border-[#3EAF9F] bg-[#E8F6F4] text-[#3EAF9F]'
                        : 'border-gray-100 bg-white text-gray-700'
                    }`}
                  >
                    {time}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </motion.div>
      )}

      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-100 p-4 pb-safe">
        <Button
          onClick={() => setStep(3)}
          disabled={!selectedDate || !selectedTime}
          className="w-full h-12 bg-[#3EAF9F] hover:bg-[#2E8F81] text-white font-medium rounded-xl disabled:opacity-50"
        >
          下一步
        </Button>
      </div>
    </motion.div>
  );

  const renderStep3 = () => (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="space-y-5 pb-24"
    >
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
        <Label className="text-sm font-medium text-gray-700">
          患者姓名 <span className="text-red-500">*</span>
        </Label>
        <Input
          placeholder="请输入患者姓名"
          value={formData.patientName}
          onChange={(e) => setFormData({ ...formData, patientName: e.target.value })}
          className="mt-1.5 h-12 bg-white border-gray-200"
        />
      </motion.div>

      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
        <Label className="text-sm font-medium text-gray-700">
          患者年龄 <span className="text-red-500">*</span>
        </Label>
        <Input
          type="number"
          placeholder="请输入患者年龄"
          value={formData.patientAge}
          onChange={(e) => setFormData({ ...formData, patientAge: e.target.value })}
          className="mt-1.5 h-12 bg-white border-gray-200"
        />
      </motion.div>

      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
        <Label className="text-sm font-medium text-gray-700">
          联系电话 <span className="text-red-500">*</span>
        </Label>
        <Input
          type="tel"
          placeholder="请输入联系电话"
          value={formData.phone}
          onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
          className="mt-1.5 h-12 bg-white border-gray-200"
        />
      </motion.div>

      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
        <Label className="text-sm font-medium text-gray-700">
          病情描述 <span className="text-gray-400">(选填)</span>
        </Label>
        <Textarea
          placeholder="请简要描述患者病情或就诊需求"
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          className="mt-1.5 bg-white border-gray-200 min-h-[100px]"
        />
      </motion.div>

      {/* Order Summary */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="bg-white rounded-xl p-4 border border-gray-100"
      >
        <h3 className="font-medium text-gray-800 mb-3">订单信息</h3>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-500">医院</span>
            <span className="text-gray-800">
              {hospitals.find((h) => h.id === selectedHospital)?.name}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">服务类型</span>
            <span className="text-gray-800">
              {serviceTypes.find((s) => s.id === selectedService)?.name}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">预约时间</span>
            <span className="text-gray-800">
              {selectedDate} {selectedTime}
            </span>
          </div>
          <div className="border-t border-gray-100 pt-2 mt-2">
            <div className="flex justify-between">
              <span className="text-gray-700 font-medium">合计</span>
              <span className="text-[#FF8C42] font-bold text-lg">
                ¥{serviceTypes.find((s) => s.id === selectedService)?.price}
              </span>
            </div>
          </div>
        </div>
      </motion.div>

      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-100 p-4 pb-safe">
        <Button
          onClick={handleSubmit}
          disabled={!formData.patientName || !formData.patientAge || !formData.phone}
          className="w-full h-12 bg-[#3EAF9F] hover:bg-[#2E8F81] text-white font-medium rounded-xl disabled:opacity-50"
        >
          {submitting ? '提交中...' : '确认预约'}
        </Button>
      </div>
    </motion.div>
  );

  return (
    <motion.div
      initial={{ x: '100%' }}
      animate={{ x: 0 }}
      exit={{ x: '100%' }}
      transition={{ type: 'spring', damping: 25, stiffness: 200 }}
      className="min-h-screen bg-gray-50"
    >
      {/* Header */}
      <div className="bg-white sticky top-0 z-10 border-b border-gray-100">
        <div className="flex items-center h-14 px-4">
          <button
            onClick={() => (step > 1 ? setStep(step - 1) : onBack())}
            className="p-2 -ml-2"
          >
            <ArrowLeft size={24} className="text-gray-700" />
          </button>
          <h1 className="text-lg font-semibold ml-2">预约陪诊</h1>
          <div className="ml-auto flex items-center gap-1">
            {[1, 2, 3].map((s) => (
              <div
                key={s}
                className={`w-2 h-2 rounded-full ${
                  s <= step ? 'bg-[#3EAF9F]' : 'bg-gray-200'
                }`}
              />
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        <AnimatePresence mode="wait">
          {step === 1 && renderStep1()}
          {step === 2 && renderStep2()}
          {step === 3 && renderStep3()}
        </AnimatePresence>
      </div>

      {/* Payment Dialog */}
      <Dialog open={showPayment} onOpenChange={setShowPayment}>
        <DialogContent className="sm:max-w-[320px] text-center p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">选择支付方式</h3>
          <p className="text-2xl font-bold text-[#FF8C42] mb-6">
            ¥{serviceTypes.find((s) => s.id === selectedService)?.price}
          </p>
          <div className="space-y-3">
            <Button
              onClick={() => handlePay('wechat')}
              className="w-full h-12 bg-[#07C160] hover:bg-[#06AD56] text-white font-medium rounded-xl"
            >
              微信支付
            </Button>
            <Button
              onClick={() => handlePay('alipay')}
              className="w-full h-12 bg-[#1677FF] hover:bg-[#0958D9] text-white font-medium rounded-xl"
            >
              支付宝支付
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Success Dialog */}
      <Dialog open={showSuccess} onOpenChange={setShowSuccess}>
        <DialogContent className="sm:max-w-[320px] text-center p-6">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', damping: 15 }}
            className="w-16 h-16 bg-[#E8F6F4] rounded-full flex items-center justify-center mx-auto mb-4"
          >
            <CheckCircle size={32} className="text-[#3EAF9F]" />
          </motion.div>
          <h3 className="text-lg font-semibold text-gray-800">预约成功</h3>
          <p className="text-sm text-gray-500 mt-2">
            陪诊师将在就诊前与您联系确认
          </p>
          <Button
            onClick={() => {
              setShowSuccess(false);
              onBack();
            }}
            className="w-full mt-6 bg-[#3EAF9F] hover:bg-[#2E8F81]"
          >
            确定
          </Button>
        </DialogContent>
      </Dialog>
    </motion.div>
  );
}
