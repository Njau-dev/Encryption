import { KeyIcon, LockClosedIcon, LockOpenIcon } from '@heroicons/react/24/outline'
import React from 'react'
import { Link } from 'react-router-dom'

const Home = () => {
    return (
        <div className="hero min-h-[60vh] glass rounded-lg w-80 md:min-w-96 lg:min-w-[1024px] lg:min-h-[90vh] border border-info shadow-2xl">
            <div className="hero-overlay bg-opacity-0"></div>
            <div className="hero-content text-neutral-content text-center">
                <div className="w-max h-max flex flex-col gap-10">
                    <h1 className="mb-5 text-5xl font-bold text-gray-700">Hello there</h1>

                    <div className='flex gap-4 items-center'>

                        <Link to='/encrypt'>
                            <div className="card bg-base-300 glass image-full w-72 hover:shadow-lg border border-info hover:scale-105 transition-all">
                                <figure>
                                    <KeyIcon className='size-36 m-8 text-info' />
                                </figure>
                                <div className="card-body">
                                    <h2 className="card-title text-info">Encrypt</h2>
                                </div>
                            </div>
                        </Link>

                        <Link to='/decrypt'>
                            <div className="card bg-base-300 glass image-full w-72 hover:shadow-lg border border-info hover:scale-105 transition-all">
                                <figure>
                                    <LockOpenIcon className='size-36 m-8 text-info' />
                                </figure>
                                <div className="card-body">
                                    <h2 className="card-title text-info">Decrypt</h2>
                                </div>
                            </div>
                        </Link>

                    </div>
                </div>
            </div>
        </div>
    )
}

export default Home
