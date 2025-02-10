import { KeyIcon, LockOpenIcon } from '@heroicons/react/24/outline'
import { Link } from 'react-router-dom'

const Home = () => {
    return (
        <div className="hero min-h-[75vh] glass rounded-lg w-[95vw] max-w-6xl lg:min-h-[90vh] border border-info shadow-2xl mx-auto relative">
            <div className="hero-overlay bg-opacity-0"></div>
            <div className="hero-content text-neutral-content text-center p-4">
                <div className="w-full h-full flex flex-col gap-8">
                    <h1 className="text-5xl font-bold text-gray-200 mb-4">
                        Secure Vault
                    </h1>

                    <div className='flex flex-col md:flex-row gap-6 items-center justify-center w-full'>
                        <Link to='/encrypt' className="w-full max-w-[95%] sm:max-w-2xl lg:max-w-4xl">
                            <div className="card glass hover:shadow-md border border-info hover:scale-105 hover:shadow-info transition-all w-full min-h-24 md:min-h-48 flex flex-row md:flex-col lg:flex-row items-center justify-between p-6 md:p-8">
                                <KeyIcon className='size-16 md:size-20 lg:size-24 text-info flex-shrink-0' />
                                <h2 className="text-xl md:text-2xl lg:text-2xl font-semibold text-info ml-4 md:ml-0 md:mt-4 lg:mt-0 lg:ml-8">
                                    Encrypt data
                                </h2>
                            </div>
                        </Link>

                        <Link to='/decrypt' className="w-full max-w-[95%] sm:max-w-2xl lg:max-w-4xl">
                            <div className="card glass hover:shadow-md border border-info hover:scale-105 hover:shadow-info transition-all w-full min-h-24 md:min-h-48 flex flex-row md:flex-col lg:flex-row items-center justify-between p-6 md:p-8">
                                <LockOpenIcon className='size-16 md:size-20 lg:size-24 text-info flex-shrink-0' />
                                <h2 className="text-xl md:text-xl lg:text-2xl font-semibold text-info ml-4 md:ml-0 md:mt-4 lg:mt-0 lg:ml-8">
                                    Decrypt data
                                </h2>
                            </div>
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Home