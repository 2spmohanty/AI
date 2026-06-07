export async function getCurrentWeather({ location, unit = "fahrenheit" }) {
    const weather = {
        location,
        temperature: "75",
        unit,
        forecast: "sunny"
    }
    return JSON.stringify(weather)
}

export async function getLocation() {
    return "San Diego, CA"
}

export const tools = [
    {
        type: "function",
        name: "getCurrentWeather", // Moved to root level
        description: "Get the current weather", // Moved to root level
        parameters: { // Moved to root level
            type: "object",
            properties: {
                location: {
                    type: "string",
                    description: "The location from where to get the weather"
                },
                unit: {
                    type: "string",
                    enum: ["celsius", "fahrenheit"]
                }
            },
            required: ["location"]
        }
    },
    {
        type: "function",
        name: "getLocation", // Moved to root level
        description: "Get the user's current location", // Moved to root level
        parameters: { // Moved to root level
            type: "object",
            properties: {}
        }
    }
];
