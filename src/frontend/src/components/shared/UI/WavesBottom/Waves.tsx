import React from "react";
import { ReactComponent as Wave } from "../../../../assets/wave.svg";
import { ReactComponent as Wave2 } from "../../../../assets/wave_2.svg";
import { ReactComponent as Wave3 } from "../../../../assets/wave_3.svg";
export default function WavesBottom() {
  return (
    <>
      <div className="waves">
        <Wave3 className="wave3" />
        <Wave2 className="wave2" />
        <Wave className="wave" />
      </div>
    </>
  );
}
