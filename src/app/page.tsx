// "use client";
// import { useState } from "react";
// import SearchBar from "./components/SearchBar";
// import Dropdown from "./components/Dropdown";
// import { dummyData } from "./data/dummyData";

// export default function Home() {
//     const [searchQuery, setSearchQuery] = useState("");
//     const [dropdownVisible, setDropdownVisible] = useState(false);

//     // Filtered results based on search query
//     const filteredManagers = dummyData.managers.filter((item) =>
//         item.toLowerCase().includes(searchQuery.toLowerCase())
//     );
//     const filteredInvestments = dummyData.investments.filter((item) =>
//         item.toLowerCase().includes(searchQuery.toLowerCase())
//     );

//     // Handle input change
//     const handleInputChange = (e) => {
//         setSearchQuery(e.target.value);
//         setDropdownVisible(e.target.value.length > 0); // Show dropdown if there's input
//     };

//     return (
//         <div className="bg-gray-100">
//             <div className="flex flex-col h-screen md:min-w-max">
//                 <div className="flex-1 p-3 sm:p-8 md:mt-14">
//                     <div className="flex flex-col w-full sm:max-w-xl h-full mx-auto">
//                         <h1 className="mt-22 mb-4 text-[28px] font-medium leading-[45px] text-[#21385F] sm:mt-32 sm:text-5xl">
//                             Search 13F Filings
//                         </h1>
//                         <div className="relative mb-12">
//                             {/* SearchBar Component */}
//                             <SearchBar
//                                 searchQuery={searchQuery}
//                                 handleInputChange={handleInputChange}
//                             />
//                             {/* Dropdown Component */}
//                             {dropdownVisible && (
//                                 <Dropdown
//                                     filteredManagers={filteredManagers}
//                                     filteredInvestments={filteredInvestments}
//                                 />
//                             )}
//                         </div>
//                     </div>
//                 </div>
//             </div>
//         </div>
//     );
// }

'use client'

import React, { useState, useEffect } from "react";
import axios from "axios";
import SearchBar from "./components/SearchBar";
import Dropdown from "./components/Dropdown";

const Home = () => {
    const [searchQuery, setSearchQuery] = useState("");
    const [filteredManagers, setFilteredManagers] = useState([]);
    const [filingsByManager, setFilingsByManager] = useState({});
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const fetchFilings = async (filerName) => {
        try {
            setLoading(true);
            setError("");
            const response = await axios.get(`http://127.0.0.1:8000/filings/${filerName}`);
            const filings = response.data;

            // Group filings by filer_name (manager name)
            const groupedFilings = filings.reduce((acc, filing) => {
                const { filer_name } = filing;
                if (!acc[filer_name]) acc[filer_name] = [];
                acc[filer_name].push(filing);
                return acc;
            }, {});

            // Update state with filtered managers and filings
            setFilteredManagers(Object.keys(groupedFilings));
            setFilingsByManager(groupedFilings);
        } catch (err) {
            setError(err.response?.data?.detail || "Error fetching data");
        } finally {
            setLoading(false);
        }
    };

    // Handle search input change
    const handleInputChange = (e) => {
        const query = e.target.value;
        setSearchQuery(query);

        if (query.length > 0) {
            fetchFilings(query);
        } else {
            setFilteredManagers([]);
            setFilingsByManager({});
        }
    };

    return (
        <div className="bg-gray-100 h-screen">
            <div className="flex flex-col items-center justify-center">
                <h1 className="text-3xl font-bold mb-6">Search Filings by Manager</h1>
                <SearchBar searchQuery={searchQuery} handleInputChange={handleInputChange} />
                <div className="relative w-full max-w-xl mt-4">
                    {loading && <p>Loading...</p>}
                    {error && <p className="text-red-500">{error}</p>}
                    {!loading && !error && (
                        <Dropdown filteredManagers={filteredManagers} filings={filingsByManager} />
                    )}
                </div>
            </div>
        </div>
    );
};

export default Home;