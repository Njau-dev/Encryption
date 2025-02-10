import { LockClosedIcon } from "@heroicons/react/24/outline";

const Spinner = () => {
    return (
        <div className="absolute inset-0 backdrop-blur-sm bg-black bg-opacity-50 glass z-50 transition-all duration-300 rounded-lg">
            <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">
                <div className="flex flex-col items-center gap-4">
                    {/* Shield spinner */}
                    <div className="relative">
                        <div className="size-12 border-4 border-info rounded-full animate-spin border-t-transparent"></div>
                        <LockClosedIcon className="size-6 text-info absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 animate-pulse" />
                    </div>

                    {/* Animated text */}
                    <div className="flex gap-2">
                        <span className="text-info font-semibold text-xl animate-pulse">
                            Securing Data
                        </span>
                        <div className="flex gap-1">
                            <div className="size-1.5 bg-info rounded-full animate-bounce delay-100"></div>
                            <div className="size-1.5 bg-info rounded-full animate-bounce delay-200"></div>
                            <div className="size-1.5 bg-info rounded-full animate-bounce delay-300"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Spinner;