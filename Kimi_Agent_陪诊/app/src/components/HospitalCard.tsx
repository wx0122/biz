import { motion } from 'framer-motion';
import { MapPin } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import type { Hospital } from '@/types';

interface HospitalCardProps {
  hospital: Hospital;
  index: number;
}

export function HospitalCard({ hospital, index }: HospitalCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1, duration: 0.4 }}
      className="flex-shrink-0 w-[200px] bg-white rounded-xl overflow-hidden shadow-sm border border-gray-100"
      whileTap={{ scale: 0.98 }}
    >
      <div className="h-[80px] overflow-hidden">
        <img
          src={hospital.image}
          alt={hospital.name}
          className="w-full h-full object-cover"
        />
      </div>
      <div className="p-3">
        <h3 className="font-medium text-sm text-gray-800 truncate">{hospital.name}</h3>
        <div className="flex items-center justify-between mt-2">
          <Badge variant="secondary" className="text-[10px] bg-[#E8F6F4] text-[#3EAF9F] hover:bg-[#E8F6F4]">
            {hospital.level}
          </Badge>
          <div className="flex items-center text-[11px] text-gray-400">
            <MapPin size={10} className="mr-0.5" />
            {hospital.distance}
          </div>
        </div>
      </div>
    </motion.div>
  );
}
