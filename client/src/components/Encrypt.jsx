import React, { useState } from "react";
import axios from "axios";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { ClipboardIcon } from "@heroicons/react/24/outline";
import Spinner from "./Spinner";

const Encrypt = () => {

    const [pin, setPin] = useState("");
    const [text, setText] = useState("");
    const [file, setFile] = useState(null);
    const [expiryTime, setExpiryTime] = useState("");

    // State for submission status
    const [isLoading, setIsLoading] = useState(false);
    const [response, setResponse] = useState(null);

    const validateInputs = () => {
        if (!pin || !expiryTime) {
            toast.error("PIN and Expiry Time are required.");
            return false;
        }
        if (expiryTime < 30 || expiryTime > 2880) {
            toast.error("Expiry time must be between 30 and 2880 minutes.");
            return false;
        }
        if (file && file.size > 10 * 1024 * 1024) {
            toast.error("File size exceeds the 10MB limit.");
            return false;
        }
        return true;
    };

    // Handle form submission
    const handleEncrypt = async (e) => {
        e.preventDefault();
        if (!validateInputs()) return;

        setIsLoading(true);
        setResponse(null);

        try {
            // Prepare FormData
            const formData = new FormData();
            formData.append("pin", pin);
            formData.append("data", text);
            formData.append("file", file);
            formData.append("expiry_time", expiryTime);

            // Send POST request
            const res = await axios.post("https://encryption-bs0w.onrender.com/encrypt", formData);
            setResponse(res.data); // Save response data

            toast.success("Data encrypted successfully!");
            resetForm();
        } catch (err) {
            toast.error(err.response?.data?.error || "An unexpected error occurred");
        } finally {
            setIsLoading(false);
        }
    };

    // Reset the form fields
    const resetForm = () => {
        setPin("");
        setText("");
        setFile(null);
        setExpiryTime("");
    };

    // Copy key to clipboard
    const copyToClipboard = (key) => {
        navigator.clipboard.writeText(key);
        toast.info("Key copied to clipboard!");
    };

    return (
        <div className="hero min-h-[75vh] glass rounded-lg w-[95vw] max-w-6xl lg:min-h-[90vh] border border-info shadow-2xl mx-auto relative">
            <div className="hero-content text-neutral-content text-center flex flex-col items-center lg:min-w-[550px]">
                <div className="w-full ">
                    <h1 className="mb-8 text-4xl font-bold text-white">Encrypt Data</h1>
                    <form
                        onSubmit={handleEncrypt}
                        className="space-y-6 text-left">

                        {/* File Upload */}
                        <div>
                            <label htmlFor="file" className="block text-sm font-medium text-gray-200 pb-2">
                                File (Optional, max 10MB)
                            </label>
                            <input
                                type="file"
                                name="file"
                                onChange={(e) => setFile(e.target.files[0])}
                                className="file-input glass file-input-info w-full text-gray-100"
                            />
                        </div>

                        {/* Text Input */}
                        <div>
                            <label htmlFor="data" className="block font-medium text-gray-200 pb-2">
                                Text
                            </label>
                            <textarea
                                id="data"
                                name="data"
                                onChange={(e) => setText(e.target.value)}
                                value={text}
                                className="textarea textarea-info textarea-bordered glass text-gray-100 w-full"
                                placeholder="Enter text to encrypt"
                                rows={4}
                            ></textarea>
                        </div>

                        {/* PIN Input */}
                        <div>
                            <label htmlFor="pin" className="block text-sm font-medium text-gray-200 pb-2">
                                PIN <span className="text-red-500">*</span>
                            </label>
                            <input
                                type="password"
                                value={pin}
                                name="pin"
                                onChange={(e) => setPin(e.target.value)}

                                className="input input-bordered glass input-info w-full text-gray-100"
                                placeholder="Enter a secure PIN"
                                required
                            />
                        </div>

                        {/* Expiry Time */}
                        <div>
                            <label htmlFor="expiry" className="block text-sm font-medium text-gray-200 pb-2">
                                Expiry Time (Minutes) <span className="text-red-500">*</span>
                            </label>
                            <input
                                type="number"
                                id="expiry"
                                name="expiry"
                                value={expiryTime}
                                onChange={(e) => setExpiryTime(e.target.value)}
                                className="input input-bordered input-info glass w-full text-gray-100"
                                placeholder="Enter expiry time (30mins - 48hrs)"
                                min={30}
                                max={2880}
                                required
                            />
                            <p className="text-xs text-gray-200 mt-1">
                                Must be between 30 minutes and 48 hours (2880 minutes).
                            </p>
                        </div>

                        {/* Submit Button */}
                        <div>
                            <button
                                type="submit"
                                className="btn btn-info w-full"
                                disabled={isLoading}
                            >
                                Encrypt Data
                            </button>
                        </div>
                    </form>
                </div>

                {/* Modal for Response */}
                {response && (
                    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
                        <div className="bg-gray-700 rounded-lg shadow-lg p-6 w-96 lg:w-[60%]">
                            <h3 className="font-bold text-lg text-info my-4">Encryption Successful!</h3>
                            <div className="flex flex-col items-center mb-4 overflow-hidden rounded">
                                <p className="py-4 bg-gray-900 p-2 rounded text-gray-50 mb-2">
                                    <strong>Key:</strong> {response.key}{" "}
                                </p>
                                <div
                                    onClick={() => copyToClipboard(response.key)} className="flex items-center cursor-pointer mt-2">
                                    <p className="text-sm hover:text-info">Copy key to clipboard</p>
                                    <ClipboardIcon
                                        className="inline cursor-pointer ml-2 size-7 text-info"
                                    />
                                </div>
                            </div>

                            <p className="bg-gray-900 p-3 rounded text-gray-50">
                                <strong>Expiry Time:</strong> {response.expiry_time} minutes
                            </p>
                            <div className="modal-action">
                                <button
                                    className="btn text-red-500"
                                    onClick={() => setResponse(null)}
                                >
                                    Close
                                </button>
                            </div>
                        </div>
                    </div>
                )}

                {/* Toast Notifications */}
                <ToastContainer />
            </div>
            {isLoading && <Spinner />}
        </div>
    );
};

export default Encrypt;
