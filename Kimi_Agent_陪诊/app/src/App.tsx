import { useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { Home } from './pages/Home';
import { Training } from './pages/Training';
import { Booking } from './pages/Booking';
import { Orders } from './pages/Orders';
import { Profile } from './pages/Profile';
import { BottomNav } from './components/BottomNav';
import './App.css';

function App() {
  const [currentPage, setCurrentPage] = useState('home');

  const handlePageChange = (page: string) => {
    setCurrentPage(page);
  };

  const handleBackToHome = () => {
    setCurrentPage('home');
  };

  return (
    <div className="min-h-screen bg-gray-50 max-w-md mx-auto relative overflow-hidden">
      <AnimatePresence mode="wait">
        {currentPage === 'home' && (
          <motion.div
            key="home"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <Home onPageChange={handlePageChange} />
          </motion.div>
        )}

        {currentPage === 'training' && (
          <motion.div
            key="training"
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="absolute inset-0 z-20"
          >
            <Training onBack={handleBackToHome} />
          </motion.div>
        )}

        {currentPage === 'booking' && (
          <motion.div
            key="booking"
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="absolute inset-0 z-20"
          >
            <Booking onBack={handleBackToHome} />
          </motion.div>
        )}

        {currentPage === 'orders' && (
          <motion.div
            key="orders"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <Orders />
          </motion.div>
        )}

        {currentPage === 'profile' && (
          <motion.div
            key="profile"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <Profile />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Bottom Navigation - only show on main pages */}
      {['home', 'orders', 'profile'].includes(currentPage) && (
        <BottomNav currentPage={currentPage} onPageChange={handlePageChange} />
      )}
    </div>
  );
}

export default App;
