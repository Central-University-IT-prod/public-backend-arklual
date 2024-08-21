import React, { useState, useEffect } from 'react';
import { MainButton, WebAppProvider, useWebApp } from '@vkruglikov/react-telegram-web-app';
import Select from 'react-dropdown-select';

const CountryCitySelect = () => {
    const [countries, setCountries] = useState([]);
    const [cities, setCities] = useState([]);
    const [selectedCountry, setSelectedCountry] = useState('');
    const [selectedCity, setSelectedCity] = useState('');
    const webApp = useWebApp();

    useEffect(() => {
        fetch('countries.json')
            .then(response => response.json())
            .then(data => setCountries(data));
    }, []);

    const handleCountryChange = (selectedOptions) => {
        setSelectedCountry(selectedOptions[0]); 
        setSelectedCity([]);
    
        if (selectedOptions.length > 0) {
            const country = selectedOptions[0].value;
            fetch(`countries/${country}.json`)
                .then(response => response.json())
                .then(data => {
                    const uniqueCities = removeDuplicates(data, 'title');
                    setCities(uniqueCities);
                    setSelectedCity([]);
                });
        } else {
            setCities([]);
        }
    };
    
    const removeDuplicates = (arr, key) => {
        return arr.filter((obj, index, self) =>
            index === self.findIndex((o) => (
                o[key] === obj[key]
            ))
        );
    };

    const handleCityChange = (selectedOptions) => {
        setSelectedCity(selectedOptions[0]);
    };

    const handleMainButton = () => {
        let lat = '';
        let long = '';
        for (let i = 0; i < cities.length; i++) {
            if (cities[i].title === selectedCity.value) {
                lat = cities[i].lat;
                long = cities[i].long;
                break;
            }
        }
        webApp?.sendData(lat + '|' + long + '|' + selectedCity.value + '|' + selectedCountry.value);
    }

    const countryOptions = countries.map(country => ({ value: country, label: country }));
    const cityOptions = cities.map(city => ({ value: city.title, label: city.title }));
    const searchFn = ({ props, state, methods }) => {
        const query = state.search;
        const options = props.options;
        if (!Array.isArray(options) || typeof query !== 'string') {
            return [];
        }
        const filteredOptions = options.filter(option => {
            if (option && option.label) {
                const lowercaseLabel = option.label.toLowerCase();
                return lowercaseLabel.startsWith(query.toLowerCase());
            }
            return false;
        });
        const sortedOptions = filteredOptions.sort((a, b) => {
            const labelA = a.label.toLowerCase();
            const labelB = b.label.toLowerCase();
            if (labelA < labelB) {
                return -1;
            }
            if (labelA > labelB) {
                return 1;
            }
            return 0;
        });
        return sortedOptions;
    };
    
    

    return (
        <WebAppProvider>
            <div className="select-container">
                <Select
                    options={countryOptions}
                    onChange={handleCountryChange}
                    placeholder="Выберите страну"
                    sortBy="label"
                    searchFn={searchFn}
                />

                <Select
                    options={cityOptions}
                    onChange={handleCityChange}
                    placeholder="Выберите город"
                    sortBy="label"
                    searchFn={searchFn}
                />
            </div>
            <MainButton onClick={handleMainButton} text="Отправить" />
        </WebAppProvider>
    );
};

export default CountryCitySelect;

