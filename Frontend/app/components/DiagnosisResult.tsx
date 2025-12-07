"use client";

import dynamic from "next/dynamic";

// load ApexCharts cuma di client
const ReactApexChart = dynamic(() => import("react-apexcharts"), {
  ssr: false,
});

type DiagnosisItem = {
  name: string;
  value: number;
};

const diagnosisData: DiagnosisItem[] = [
  { name: "Sinusitis", value: 75 },
  { name: "Pneumonia", value: 35 },
  { name: "Bronkitis", value: 56 },
];

export default function DiagnosisResult() {
  return (
    <section className="mt-10 mb-4">
      <h2 className="text-center text-lg font-semibold text-gray-800 mb-8">
        Hasil Diagnosa
      </h2>

      <div className="flex flex-wrap justify-center gap-8">
        {diagnosisData.map((item, i) => (
          <DiagnosisCard key={i} name={item.name} value={item.value} />
        ))}
      </div>
    </section>
  );
}

type CardProps = {
  name: string;
  value: number;
};

function DiagnosisCard({ name, value }: CardProps) {
  const series = [value];

  const options: any = {
    chart: {
      type: "radialBar",
      sparkline: { enabled: true },
    },
    plotOptions: {
      radialBar: {
        startAngle: -135,
        endAngle: 135,
        hollow: {
          size: "65%",
        },
        track: {
          background: "#f3f4ff",
          strokeWidth: "90%",
          margin: 4,
          dropShadow: {
            enabled: true,
            top: 2,
            blur: 4,
            opacity: 0.18,
          },
        },
        dataLabels: {
          show: true,
          name: {
            show: true,
            offsetY: -10,
            color: "#60a5fa",
            fontSize: "12px",
          },
          value: {
            show: true,
            fontSize: "24px",
            fontWeight: 500,
            color: "#111827",
          },
        },
      },
    },
    labels: ["Percentage"],
    fill: {
      type: "gradient",
      gradient: {
        shade: "light",
        type: "horizontal",
        gradientToColors: ["#3b82f6"],
        stops: [0, 50, 100],
      },
      colors: ["#6ee7b7"],
    },
    stroke: {
      lineCap: "round",
    },
  };

  return (
    <div className="w-72 h-72 bg-white/90 rounded-3xl shadow-xl flex flex-col items-center justify-center">
      <div className="w-48 h-48 flex items-center justify-center">
        <ReactApexChart
          options={options}
          series={series}
          type="radialBar"
          height={200}
          width={200}
        />
      </div>
      <div className="mt-2 text-sm font-medium text-gray-800">{name}</div>
    </div>
  );
}