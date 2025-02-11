import { motion } from 'framer-motion';
import { Link, useLocation } from 'react-router-dom';
import { GrInsecure, GrSecure } from 'react-icons/gr';
import { RiHome5Line } from 'react-icons/ri';
import { TopBar } from './TopBar';

const Layout = ({ children }) => {
    const location = useLocation();

    const navLinks = [
        { path: '/', label: 'Home', icon: <RiHome5Line className="size-5" /> },
        { path: '/encrypt', label: 'Encrypt', icon: <GrSecure className="size-5" /> },
        { path: '/decrypt', label: 'Decrypt', icon: <GrInsecure className="size-5" /> },
    ];

    return (
        <div className="min-h-screen flex flex-col">
            <TopBar />
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
                <div className="join backdrop-blur-lg bg-transparent rounded-lg  shadow-lg border border-info">
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