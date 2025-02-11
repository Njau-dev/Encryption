import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';
import { BsShieldLock } from 'react-icons/bs';
import { GrSecure } from 'react-icons/gr';
import { SlClock } from 'react-icons/sl';

const CipherVisualization = ({ isMobile, isLoading }) => {
    return (
        <div className="relative h-16 w-48 md:h-12 md:w-64">
            {/* Desktop: Wide rotating disc */}
            <div className="hidden md:hidden">
                <div className="relative h-full w-full animate-rotate3d">
                    <div className="relative inset-0 flex items-center justify-center">
                        {/* Rotating segments with border */}
                        <div className={`absolute h-full w-full rounded-full border-2 ${isLoading ? 'border-warning' : 'border-info'
                            } opacity-30 animate-spin-slow`} />

                        {/* Central icon */}
                        <GrSecure className={`h-8 w-8 ${isLoading ? 'text-warning animate-pulse' : 'text-info'
                            } transition-colors duration-300 `} />
                    </div>
                </div>
            </div>
        </div>
    );
};

const TimeIndicator = () => {
    const [time, setTime] = useState(new Date());

    useEffect(() => {
        const timer = setInterval(() => setTime(new Date()), 1000);
        return () => clearInterval(timer);
    }, []);

    return (
        <motion.div
            className="flex items-center gap-2"
            whileHover={{ scale: 1.05 }}
        >
            <div className="relative">
                <SlClock className="h-6 w-6 text-info animate-pulse" />
                <div className="absolute inset-0 border-2 border-info rounded-full animate-rotateBorder" />
            </div>
            <span className="font-mono text-info">
                {time.toLocaleTimeString('en-US', {
                    hour: '2-digit',
                    minute: '2-digit'
                })}
            </span>
        </motion.div>
    );
};

export const TopBar = () => {
    return (
        <div className="w-[95vw] max-w-6xl flex items-center justify-between px-4 md:px-12 py-3 rounded-lg sticky top-3">
            {/* Left: Shield Animation */}
            <motion.div
                className="flex items-center gap-2"
                transition={{
                    duration: 2,
                    repeat: Infinity,
                    repeatType: 'reverse'
                }}
            >
                <BsShieldLock className="h-8 w-8 text-info" />
            </motion.div>

            {/* Center: Cipher Visualization */}
            <CipherVisualization />

            {/* Right: Time Indicator */}
            <TimeIndicator />
        </div>
    );
};