import { useState } from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft, CheckCircle, Award, Users, BookOpen, Briefcase } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Dialog, DialogContent } from '@/components/ui/dialog';
import { trainingApi, paymentApi } from '@/lib/api';

interface TrainingProps {
  onBack: () => void;
}

const courses = [
  { id: '1', name: '基础培训班', price: 1980, duration: '7天', description: '适合零基础学员' },
  { id: '2', name: '进阶提升班', price: 2980, duration: '14天', description: '提升专业技能' },
  { id: '3', name: '全能精英班', price: 4980, duration: '30天', description: '全面系统培训' },
];

const highlights = [
  { icon: Award, title: '权威证书', desc: '结业颁发国家认可证书' },
  { icon: Users, title: '专业师资', desc: '资深医疗专家授课' },
  { icon: BookOpen, title: '实操训练', desc: '真实场景模拟演练' },
  { icon: Briefcase, title: '就业推荐', desc: '优秀学员推荐就业' },
];

export function Training({ onBack }: TrainingProps) {
  const [formData, setFormData] = useState({
    name: '',
    phone: '',
    course: '1',
    remark: '',
  });
  const [showSuccess, setShowSuccess] = useState(false);
  const [showPayment, setShowPayment] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [lastRegId, setLastRegId] = useState<number | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const res = await trainingApi.register({
        course_id: parseInt(formData.course),
        name: formData.name,
        phone: formData.phone,
        remark: formData.remark,
      });
      setLastRegId(res.registration?.id || null);
      setShowPayment(true);
    } catch {
      setShowSuccess(true);
    } finally {
      setSubmitting(false);
    }
  };

  const handlePay = async (method: 'wechat' | 'alipay') => {
    if (!lastRegId) return;
    try {
      const res = await paymentApi.create({
        order_type: 'training',
        order_id: lastRegId,
        method,
      });
      if (res.pay_url && !res.pay_url.startsWith('mock://')) {
        window.location.href = res.pay_url;
      } else {
        setShowPayment(false);
        setShowSuccess(true);
      }
    } catch {
      setShowPayment(false);
      setShowSuccess(true);
    }
  };

  return (
    <motion.div
      initial={{ x: '100%' }}
      animate={{ x: 0 }}
      exit={{ x: '100%' }}
      transition={{ type: 'spring', damping: 25, stiffness: 200 }}
      className="min-h-screen bg-gray-50 pb-24"
    >
      {/* Header */}
      <div className="bg-white sticky top-0 z-10 border-b border-gray-100">
        <div className="flex items-center h-14 px-4">
          <button onClick={onBack} className="p-2 -ml-2">
            <ArrowLeft size={24} className="text-gray-700" />
          </button>
          <h1 className="text-lg font-semibold ml-2">培训报名</h1>
        </div>
      </div>

      {/* Course Banner */}
      <div className="relative h-[150px] overflow-hidden">
        <img
          src="/images/banner2.jpg"
          alt="培训 banner"
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent" />
        <div className="absolute bottom-4 left-4 text-white">
          <h2 className="text-xl font-bold">陪诊师资格认证培训</h2>
          <p className="text-sm text-white/80 mt-1">专业培训 · 系统学习 · 持证上岗</p>
        </div>
      </div>

      {/* Highlights */}
      <div className="px-4 -mt-4 relative z-10">
        <div className="bg-white rounded-xl p-4 shadow-sm grid grid-cols-2 gap-4">
          {highlights.map((item, index) => {
            const Icon = item.icon;
            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="flex items-start gap-2"
              >
                <div className="w-8 h-8 bg-[#E8F6F4] rounded-lg flex items-center justify-center flex-shrink-0">
                  <Icon size={16} className="text-[#3EAF9F]" />
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-800">{item.title}</p>
                  <p className="text-[11px] text-gray-500">{item.desc}</p>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="px-4 mt-6 space-y-5">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Label htmlFor="name" className="text-sm font-medium text-gray-700">
            姓名 <span className="text-red-500">*</span>
          </Label>
          <Input
            id="name"
            placeholder="请输入您的姓名"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            className="mt-1.5 h-12 bg-white border-gray-200"
            required
          />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Label htmlFor="phone" className="text-sm font-medium text-gray-700">
            手机号 <span className="text-red-500">*</span>
          </Label>
          <Input
            id="phone"
            type="tel"
            placeholder="请输入您的手机号"
            value={formData.phone}
            onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
            className="mt-1.5 h-12 bg-white border-gray-200"
            required
          />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <Label className="text-sm font-medium text-gray-700">
            意向课程 <span className="text-red-500">*</span>
          </Label>
          <RadioGroup
            value={formData.course}
            onValueChange={(value) => setFormData({ ...formData, course: value })}
            className="mt-2 space-y-2"
          >
            {courses.map((course) => (
              <label
                key={course.id}
                className={`flex items-center justify-between p-4 rounded-xl border-2 cursor-pointer transition-all ${
                  formData.course === course.id
                    ? 'border-[#3EAF9F] bg-[#E8F6F4]'
                    : 'border-gray-100 bg-white'
                }`}
              >
                <div className="flex items-center gap-3">
                  <RadioGroupItem value={course.id} id={course.id} />
                  <div>
                    <p className="font-medium text-gray-800">{course.name}</p>
                    <p className="text-xs text-gray-500">{course.description}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-[#3EAF9F] font-semibold">¥{course.price}</p>
                  <p className="text-xs text-gray-400">{course.duration}</p>
                </div>
              </label>
            ))}
          </RadioGroup>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <Label htmlFor="remark" className="text-sm font-medium text-gray-700">
            备注信息 <span className="text-gray-400">(选填)</span>
          </Label>
          <Textarea
            id="remark"
            placeholder="如有其他需求请在此说明"
            value={formData.remark}
            onChange={(e) => setFormData({ ...formData, remark: e.target.value })}
            className="mt-1.5 bg-white border-gray-200 min-h-[100px]"
          />
        </motion.div>
      </form>

      {/* Submit Button */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-100 p-4 pb-safe">
        <Button
          onClick={handleSubmit}
          disabled={submitting || !formData.name || !formData.phone}
          className="w-full h-12 bg-[#3EAF9F] hover:bg-[#2E8F81] text-white font-medium rounded-xl disabled:opacity-50"
        >
          {submitting ? '提交中...' : '提交报名'}
        </Button>
      </div>

      {/* Payment Dialog */}
      <Dialog open={showPayment} onOpenChange={setShowPayment}>
        <DialogContent className="sm:max-w-[320px] text-center p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">选择支付方式</h3>
          <p className="text-2xl font-bold text-[#3EAF9F] mb-6">
            ¥{courses.find((c) => c.id === formData.course)?.price}
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
          <h3 className="text-lg font-semibold text-gray-800">报名成功</h3>
          <p className="text-sm text-gray-500 mt-2">
            我们的工作人员将在24小时内与您联系
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
