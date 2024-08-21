import React, { useState, useEffect } from 'react';
import Select from 'react-dropdown-select';
import { MainButton, WebAppProvider, useWebApp } from '@vkruglikov/react-telegram-web-app';
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.min.css";
import './App.css'

const CountryCitySelect = () => {
    const [countries, setCountries] = useState([]);
    const [cities, setCities] = useState([]);
    const [selectedCountry, setSelectedCountry] = useState('');
    const [selectedCity, setSelectedCity] = useState('');
    const [startDate, setStartDate] = useState(null);
    const [endDate, setEndDate] = useState(null);
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
        webApp?.sendData(selectedCountry['value'] + '|' + selectedCity['value'] + '|' + lat + '|' + long + '|' + startDate + '|' + endDate);
    }
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

    const countryOptions = countries.map(country => ({ value: country, label: country }));
    const cityOptions = cities.map(city => ({ value: city.title, label: city.title }));

    return (
        <WebAppProvider>
            <MainButton className="main_button_tg" onClick={handleMainButton}
                text="Отправить" />
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
            <div className="datepicker-container">
                <label>Приеду:</label>
                <DatePicker id='start-picker' selected={startDate} onChange={date => setStartDate(date)} onFocus={(e) => e.target.readOnly = true} />
                <label>Выеду:</label>
                <DatePicker id='end-picker' selected={endDate} onChange={date => setEndDate(date)} onFocus={(e) => e.target.readOnly = true} />
            </div>

        </WebAppProvider>
    );
};

export default CountryCitySelect;

