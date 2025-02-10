// Layout.tsx
import { motion } from 'framer-motion';
import { Link, useLocation } from 'react-router-dom';
import { LockClosedIcon, LockOpenIcon, KeyIcon } from '@heroicons/react/24/outline';

const Layout = ({ children }) => {
    const location = useLocation();

    const navLinks = [
        { path: '/', label: 'Home', icon: <KeyIcon className="size-5" /> },
        { path: '/encrypt', label: 'Encrypt', icon: <LockClosedIcon className="size-5" /> },
        { path: '/decrypt', label: 'Decrypt', icon: <LockOpenIcon className="size-5" /> },
    ];

    return (
        <div className="min-h-screen flex flex-col">
            <motion.div
                key={location.pathname}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.3 }}
                className="flex-1"
            >
                {children}
            </motion.div>

            {/* Animated Pagination */}
            <div className="fixed bottom-5 left-1/2 -translate-x-1/2">
                <div className="join backdrop-blur-lg bg-transparent rounded-lg p-2 shadow-lg border border-info">
                    {navLinks.map((link) => (
                        <Link
                            key={link.path}
                            to={link.path}
                            className={`join-item btn btn-sm lg:btn-md ${location.pathname === link.path
                                ? 'btn-info text-base-100'
                                : 'bg-transparent text-info hover:bg-info/20'
                                } rounded-lg transition-all duration-300`}
                        >
                            <motion.div
                                className="flex items-center gap-2"
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                            >
                                {link.icon}
                                <span className="hidden sm:inline">{link.label}</span>
                            </motion.div>
                        </Link>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default Layout;