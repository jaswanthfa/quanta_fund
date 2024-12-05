const SearchBar = ({ searchQuery, handleInputChange }) => {
    return (
        <input
            name="q"
            placeholder="Search by manager or investment.."
            value={searchQuery}
            type="search"
            onChange={handleInputChange}
            className="border-custom ml-5 mr-4 h-12 w-[335px]
                         text-black rounded border border-[#A9A9A9] p-3 placeholder:text-gray-600  focus:outline-none focus:ring-2 focus:ring-blue-500 sm:mr-0 sm:w-[350px] sm:text-xl md:ml-0 md:w-[600px]"
            autoComplete="off"
        />
    );
};

export default SearchBar;
