import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { GraduationCap, CalendarCheck, ChevronRight, MapPin } from 'lucide-react';
import { Carousel, CarouselContent, CarouselItem } from '@/components/ui/carousel';
import { HospitalCard } from '@/components/HospitalCard';
import { EscortCard } from '@/components/EscortCard';
import { hospitalApi, escortApi, cityApi } from '@/lib/api';
import type { Hospital, Escort } from '@/types';

interface HomeProps {
  onPageChange: (page: string) => void;
}

const banners = [
  { id: 1, image: '/images/banner1.jpg', alt: '专业陪诊服务' },
  { id: 2, image: '/images/banner2.jpg', alt: '陪诊师培训' },
  { id: 3, image: '/images/banner3.jpg', alt: '优惠活动' },
];

const fallbackHospitals: Hospital[] = [
  { id: '1', name: '市中心人民医院', level: '三甲', distance: '1.2km', image: '/images/hospital1.jpg' },
  { id: '2', name: '市第一人民医院', level: '三甲', distance: '2.5km', image: '/images/hospital2.jpg' },
  { id: '3', name: '市中医院', level: '三甲', distance: '3.1km', image: '/images/hospital3.jpg' },
  { id: '4', name: '市妇幼保健院', level: '二甲', distance: '4.0km', image: '/images/hospital4.webp' },
];

const fallbackEscorts: Escort[] = [
  { id: '1', name: '李芳', avatar: '/images/avatar1.jpg', rating: 4.9, serviceCount: 328, tags: ['专业', '细心'] },
  { id: '2', name: '王强', avatar: '/images/avatar2.jpg', rating: 4.8, serviceCount: 256, tags: ['经验丰富'] },
  { id: '3', name: '张敏', avatar: '/images/avatar3.jpg', rating: 4.9, serviceCount: 412, tags: ['耐心', '专业'] },
  { id: '4', name: '陈明', avatar: '/images/avatar4.jpg', rating: 4.7, serviceCount: 189, tags: ['热情'] },
];

export function Home({ onPageChange }: HomeProps) {
  const [api, setApi] = useState<any>();
  const [current, setCurrent] = useState(0);
  const [hospitals, setHospitals] = useState<Hospital[]>(fallbackHospitals);
  const [escorts, setEscorts] = useState<Escort[]>(fallbackEscorts);
  const [currentCity, setCurrentCity] = useState('');

  useEffect(() => {
    // Auto-detect city
    cityApi.detect().then((res) => {
      setCurrentCity(res.city);
      localStorage.setItem('city', res.city);
      // Load city-specific data
      hospitalApi.list({ city: res.city }).then((r) => {
        if (r.items.length > 0) setHospitals(r.items);
      }).catch(() => {});
      escortApi.list(res.city).then((r) => {
        if (r.items.length > 0) setEscorts(r.items);
      }).catch(() => {});
    }).catch(() => {
      // Fallback: load all data without city filter
      hospitalApi.list().then((r) => {
        if (r.items.length > 0) setHospitals(r.items);
      }).catch(() => {});
      escortApi.list().then((r) => {
        if (r.items.length > 0) setEscorts(r.items);
      }).catch(() => {});
    });
  }, []);

  useEffect(() => {
    if (!api) return;

    setCurrent(api.selectedScrollSnap());
    api.on('select', () => {
      setCurrent(api.selectedScrollSnap());
    });

    // Auto play
    const interval = setInterval(() => {
      api.scrollNext();
    }, 5000);

    return () => clearInterval(interval);
  }, [api]);

  return (
    <div className="pb-20">
      {/* City indicator */}
      {currentCity && (
        <div className="px-4 pt-3 flex items-center gap-1 text-sm text-gray-600">
          <MapPin size={14} className="text-[#3EAF9F]" />
          <span>{currentCity}</span>
        </div>
      )}

      {/* Banner Carousel */}
      <div className="px-4 pt-4">
        <Carousel setApi={setApi} className="w-full">
          <CarouselContent>
            {banners.map((banner) => (
              <CarouselItem key={banner.id}>
                <div className="relative h-[180px] rounded-2xl overflow-hidden">
                  <img
                    src={banner.image}
                    alt={banner.alt}
                    className="w-full h-full object-cover"
                  />
                </div>
              </CarouselItem>
            ))}
          </CarouselContent>
        </Carousel>
        
        {/* Dots indicator */}
        <div className="flex justify-center gap-2 mt-3">
          {banners.map((_, index) => (
            <div
              key={index}
              className={`w-2 h-2 rounded-full transition-all duration-300 ${
                current === index ? 'bg-[#3EAF9F] w-4' : 'bg-gray-300'
              }`}
            />
          ))}
        </div>
      </div>

      {/* Feature Buttons */}
      <div className="px-4 mt-6">
        <div className="grid grid-cols-2 gap-4">
          <motion.button
            onClick={() => onPageChange('training')}
            className="bg-[#3EAF9F] rounded-2xl p-5 text-white flex flex-col items-start"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center mb-3">
              <GraduationCap size={24} />
            </div>
            <span className="text-lg font-semibold">培训报名</span>
            <span className="text-sm text-white/80 mt-1">成为专业陪诊师</span>
          </motion.button>

          <motion.button
            onClick={() => onPageChange('booking')}
            className="bg-[#FF8C42] rounded-2xl p-5 text-white flex flex-col items-start"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center mb-3">
              <CalendarCheck size={24} />
            </div>
            <span className="text-lg font-semibold">预约陪诊</span>
            <span className="text-sm text-white/80 mt-1">专业陪护服务</span>
          </motion.button>
        </div>
      </div>

      {/* Hospital List */}
      <div className="mt-8">
        <div className="px-4 flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-800">合作医院</h2>
          <button className="flex items-center text-sm text-[#3EAF9F]">
            查看更多
            <ChevronRight size={16} />
          </button>
        </div>
        
        <div className="flex gap-3 overflow-x-auto px-4 scrollbar-hide pb-2">
          {hospitals.map((hospital, index) => (
            <HospitalCard key={hospital.id} hospital={hospital} index={index} />
          ))}
        </div>
      </div>

      {/* Recommended Escorts */}
      <div className="mt-8">
        <div className="px-4 flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-800">推荐陪诊师</h2>
          <button className="flex items-center text-sm text-[#3EAF9F]">
            查看更多
            <ChevronRight size={16} />
          </button>
        </div>
        
        <div className="flex gap-3 overflow-x-auto px-4 scrollbar-hide pb-2">
          {escorts.map((escort, index) => (
            <EscortCard key={escort.id} escort={escort} index={index} />
          ))}
        </div>
      </div>
    </div>
  );
}
