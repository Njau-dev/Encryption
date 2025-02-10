import React, { useState } from 'react';
import axios from 'axios';
import { toast, ToastContainer } from 'react-toastify';
import { CloudArrowDownIcon } from '@heroicons/react/24/outline';
import Spinner from './Spinner';

const Decrypt = () => {
    const [key, setKey] = useState('');
    const [pin, setPin] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [modalOpen, setModalOpen] = useState(false);
    const [responseData, setResponseData] = useState({
        decryptedText: null,
        decryptedFile: null,
        expiryTimeStatus: null,
    });


    const handleDecrypt = async (e) => {
        e.preventDefault();

        setIsLoading(true);
        setResponseData({ decryptedText: null, decryptedFile: null, expiryTimeStatus: null });

        try {
            const response = await axios.post('https://encryption-bs0w.onrender.com/decrypt', { key, pin });
            const { decrypted_text, decrypted_file, expiry_time_status } = response.data;

            setResponseData({
                decryptedText: decrypted_text || null,
                decryptedFile: decrypted_file || null,
                expiryTimeStatus: expiry_time_status || null,
            });

            toast.success('Decryption successful!');
            setModalOpen(true);
        } catch (error) {
            toast.error(error.response?.data?.error || 'An error occurred during decryption.');
        } finally {
            setIsLoading(false);
        }
    };

    const downloadFile = () => {
        if (!responseData.decryptedFile) {
            toast.error("No file data available for download.");
            return;
        }

        try {
            // Decode Base64 to binary data
            const binaryData = atob(responseData.decryptedFile);
            const byteArray = Uint8Array.from(binaryData, (char) => char.charCodeAt(0));

            // Determine file type (adjust MIME type as needed)
            const mimeType = "application/octet-stream"; // General binary type
            const blob = new Blob([byteArray], { type: mimeType });

            // Generate file name with appropriate extension
            const fileName = "decrypted_file.bin"; // Replace ".bin" with correct extension if known

            // Create a temporary link for download
            const link = document.createElement("a");
            link.href = URL.createObjectURL(blob);
            link.download = fileName;

            // Trigger the download
            link.click();

            // Revoke object URL to free memory
            URL.revokeObjectURL(link.href);
        } catch (error) {
            toast.error("Failed to process file for download.");
            console.error("File download error:", error);
        }
    };


    const closeModal = () => {
        setModalOpen(false);
        setResponseData({ decryptedText: null, decryptedFile: null, expiryTimeStatus: null });
    };

    return (
        <div className="hero min-h-[75vh] glass rounded-lg w-[95vw] max-w-6xl lg:min-h-[90vh] border border-info shadow-2xl mx-auto relative">
            <div className="hero-content text-neutral-content text-center flex flex-col items-center lg:min-w-[550px]">
                <div className="w-full max-w-md mx-auto">
                    <h1 className="mb-12 text-5xl font-bold text-gray-50">Decrypt</h1>
                    <form onSubmit={handleDecrypt} className="space-y-4">
                        <div>
                            <input
                                type="text"
                                placeholder="Enter Key"
                                className="input input-bordered glass text-gray-200 w-full"
                                value={key}
                                onChange={(e) => setKey(e.target.value)}
                                required
                            />
                        </div>
                        <div>
                            <input
                                type="password"
                                placeholder="Enter PIN"
                                className="input input-bordered glass text-gray-200 w-full"
                                value={pin}
                                onChange={(e) => setPin(e.target.value)}
                                required
                            />
                        </div>
                        <button
                            type="submit"
                            className={`btn btn-info w-full ${isLoading ? 'loading' : ''}`}
                            disabled={isLoading}
                        >
                            Decrypt
                        </button>
                    </form>
                </div>
            </div>

            {isLoading && <Spinner />}

            {/* Modal */}
            {modalOpen && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
                    <div className="bg-gray-700 rounded-lg shadow-lg p-6 w-96 lg:w-[60%]">
                        <h2 className="text-2xl text-info font-bold mb-4">Decrypted data</h2>
                        {responseData.decryptedText && (
                            <div className="mb-4">
                                <h3 className="text-lg font-semibold mb-2 text-gray-50">Decrypted Text:</h3>
                                <p className="p-2 bg-gray-900 text-white rounded">{responseData.decryptedText}</p>
                            </div>
                        )}

                        {responseData.decryptedFile && (
                            <div className="mb-4">
                                <h3 className="text-lg font-semibold text-gray-50">Decrypted File:</h3>
                                <div className='flex flex-col items-center cursor-pointer justify-center gap-4 bg-gray-900 rounded py-4 my-3 text-gray-50 hover:text-info' onClick={downloadFile} >
                                    <CloudArrowDownIcon className="size-10" />
                                    <p>Download File</p>
                                </div>
                            </div>
                        )}
                        {responseData.expiryTimeStatus && (
                            <div className="mb-4">
                                <h3 className="text-lg font-semibold mb-2 text-gray-50">Expiry Time Status:</h3>
                                <p className="text-gray-50 bg-gray-900 p-2 rounded">{responseData.expiryTimeStatus}</p>
                            </div>
                        )}
                        <button onClick={closeModal} className="btn btn-error w-full mt-2">
                            Close
                        </button>
                    </div>
                </div>
            )}

            <ToastContainer />
        </div>
    );
};

export default Decrypt;
