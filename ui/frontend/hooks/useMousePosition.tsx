import { useEffect, useState } from "react";

const useMousePosition = () => {
    // setup state
    const [mousePosition, setMousePosition] = useState({
        x: 0,
        y: 0,
    });

    // prepare logic for updating mouse position
    const handleMouseMove = (e: MouseEvent) => {
        setMousePosition({
            x: e.clientX,
            y: e.clientY,
        });
    };

    // add an event listener on the window component to handle mouse movements
    useEffect(() => {
        // register event listener
        window.addEventListener("mousemove", handleMouseMove);

        // clean up
        return () => {
            window.removeEventListener("mousemove", handleMouseMove);
        }
    }, [])

    return mousePosition;
};

export default useMousePosition;