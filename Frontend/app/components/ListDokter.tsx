"use client";

import React from "react";

type Doctor = {
  name: string;
  specialty?: string;
  url: string;
};

const doctors: Doctor[] = [
  {
    name: "dr. I Gede Wahyu Adi Raditya Sp.THT-KL",
    specialty: "Spesialis THT-KL",
    url: "https://halodoc.onelink.me/g7yv/5e5rr34y",
  },
  {
    name: "dr. Septianus Hermanto",
    specialty: "Dokter Umum",
    url: "https://halodoc.onelink.me/g7yv/2trjuxgm",
  },
  {
    name: "dr. Cintya Andriani",
    specialty: "Dokter Umum",
    url: "https://halodoc.onelink.me/g7yv/0urgvq6i",
  },
  {
    name: "dr. Lim Jen Siong",
    specialty: "Dokter Umum",
    url: "https://halodoc.onelink.me/g7yv/53ftdiv3",
  },
  {
    name: "dr. Haerul Saleh Sp.THT-KL",
    specialty: "Spesialis THT-KL",
    url: "https://halodoc.onelink.me/g7yv/1jmg07rv",
  },
];

function getInitials(name: string) {
  const cleaned = name
    .replace(/^dr\.\s*/i, "")
    .replace(/sp\..*$/i, "")
    .trim();
  const parts = cleaned.split(/\s+/).filter(Boolean);
  const a = parts[0]?.[0] ?? "D";
  const b = parts[1]?.[0] ?? parts[0]?.[1] ?? "R";
  return (a + b).toUpperCase();
}

export default function ListDokter() {
  return (
    <div className="mt-8">
      {/* Header kecil seperti section */}
      <div className="text-center mb-4">
        <h2 className="text-base md:text-lg font-semibold text-gray-800">
          Rekomendasi Dokter
        </h2>
        <p className="text-xs md:text-sm text-gray-500 mt-1">
          Jika gejala berlanjut, kamu bisa konsultasi ke dokter berikut.
        </p>
      </div>

      {/* Card wrapper glass */}
      <div className="bg-white/70 backdrop-blur-xl border border-white/60 rounded-3xl p-5 md:p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {doctors.map((d, idx) => (
            <div
              key={idx}
              className="bg-white/85 border border-indigo-100 rounded-2xl p-4 shadow-md hover:shadow-lg transition"
            >
              <div className="flex items-center gap-3">
                {/* Avatar */}
                <div className="w-11 h-11 rounded-2xl bg-indigo-100 border border-indigo-200 flex items-center justify-center font-bold text-indigo-500">
                  {getInitials(d.name)}
                </div>

                <div className="min-w-0 flex-1">
                  <div className="font-semibold text-gray-800 text-sm md:text-[15px] truncate">
                    {d.name}
                  </div>
                  <div className="text-xs text-gray-500 mt-0.5">
                    {d.specialty ?? "Dokter"}
                  </div>
                </div>

                {/* Badge */}
                <span className="text-[10px] px-2 py-1 rounded-full bg-indigo-50 text-indigo-600 border border-indigo-100">
                  Online
                </span>
              </div>

              <div className="mt-3 flex items-center justify-between gap-3">
                <div className="text-[11px] text-gray-500 truncate">
                  Link: <span className="text-gray-700">{d.url}</span>
                </div>

                <a
                  href={d.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="shrink-0 px-4 py-2 rounded-full bg-indigo-300 text-white text-xs font-semibold shadow-md hover:bg-indigo-400 transition"
                >
                  Konsultasi
                </a>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
