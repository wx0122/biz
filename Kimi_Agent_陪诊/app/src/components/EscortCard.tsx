import { motion } from 'framer-motion';
import { Star, UserCheck } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import type { Escort } from '@/types';

interface EscortCardProps {
  escort: Escort;
  index: number;
}

export function EscortCard({ escort, index }: EscortCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1, duration: 0.4 }}
      className="flex-shrink-0 w-[160px] bg-white rounded-xl p-4 shadow-sm border border-gray-100"
      whileTap={{ scale: 0.98 }}
    >
      <div className="flex flex-col items-center">
        <Avatar className="w-14 h-14 mb-2">
          <AvatarImage src={escort.avatar} alt={escort.name} />
          <AvatarFallback className="bg-[#E8F6F4] text-[#3EAF9F]">
            {escort.name.charAt(0)}
          </AvatarFallback>
        </Avatar>
        
        <h3 className="font-medium text-sm text-gray-800">{escort.name}</h3>
        
        <div className="flex items-center mt-1 space-x-1">
          <Star size={12} className="text-yellow-400 fill-yellow-400" />
          <span className="text-xs text-gray-600">{escort.rating}</span>
        </div>
        
        <div className="flex items-center mt-1 text-[11px] text-gray-400">
          <UserCheck size={11} className="mr-0.5" />
          <span>服务{escort.serviceCount}次</span>
        </div>
        
        <div className="flex flex-wrap justify-center gap-1 mt-2">
          {escort.tags.map((tag, i) => (
            <Badge
              key={i}
              variant="secondary"
              className="text-[9px] px-1.5 py-0 bg-[#E8F6F4] text-[#3EAF9F] hover:bg-[#E8F6F4]"
            >
              {tag}
            </Badge>
          ))}
        </div>
      </div>
    </motion.div>
  );
}
