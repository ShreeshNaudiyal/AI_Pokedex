/**
 * Thin wrapper around the backend REST API.
 * Adjust BASE_URL if your Spring Boot backend runs on a different host/port.
 */

const API = (() => {
    const BASE_URL = "http://localhost:8080/api";

    /**
     * Uploads an image file and returns the parsed PokemonResponse JSON.
     * Throws an Error with a user-facing message on failure.
     */
    async function identify(file) {
        const formData = new FormData();
        formData.append("image", file);

        let response;
        try {
            response = await fetch(`${BASE_URL}/identify`, {
                method: "POST",
                body: formData,
            });
        } catch (networkErr) {
            throw new Error("Could not reach the server. Is the backend running?");
        }

        if (!response.ok) {
            let message = "Something went wrong identifying this image.";
            try {
                const errorBody = await response.json();
                if (errorBody && errorBody.message) {
                    message = errorBody.message;
                }
            } catch (_) {
                // response wasn't JSON, keep default message
            }
            throw new Error(message);
        }

        return response.json();
    }

    return { identify };
})();