import React from "react";
import { ReactComponent as Wave } from "../../../../assets/wave.svg";
import { ReactComponent as Wave2 } from "../../../../assets/wave_2.svg";
import { ReactComponent as Wave3 } from "../../../../assets/wave_3.svg";
export default function WavesBottom() {
  return (
    <>
      <div className="waves">
        <div className="circle">
          <svg viewBox="0 0 1440 200">
            <circle cx="200" cy="200" r="200" />
          </svg>
        </div>
        <Wave3 className="wave3" />
        <Wave2 className="wave2" />
        <Wave className="wave" />
      </div>
    </>
  );
}
