// 
// simple script from
// https://github.com/hungtcs/traditional-chinese-calendar-database
// 
// by .NFC 2023/08/30
// -----------------------------------------------------------------------------
// from command prompt, run
// node convert-to-binary.js
// then, you will get all.bin, all.h
// 

"use strict";

const START_YEAR = 1980;

var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const fs_1 = __importDefault(require("fs"));
const path_1 = __importDefault(require("path"));
const TIAN_GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸'];
const DI_ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥'];
const MONTHS = ['正月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月'];
const DATES = [
    '初一', '初二', '初三', '初四', '初五', '初六', '初七', '初八', '初九', '初十',
    '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十',
    '廿一', '廿二', '廿三', '廿四', '廿五', '廿六', '廿七', '廿八', '廿九', '三十',
];
const JIE_QI = [
    '立春', '雨水', '惊蛰', '春分', '清明', '谷雨', '立夏', '小满', '芒种', '夏至', '小暑', '大暑',
    '立秋', '处暑', '白露', '秋分', '寒露', '霜降', '立冬', '小雪', '大雪', '冬至', '小寒', '大寒',
];
const jsonBasePath = path_1.default.join(__dirname, './min');
const newData = [];
for (let i = START_YEAR; i <= 2100; i++) {
    const json = fs_1.default.readFileSync(path_1.default.join(jsonBasePath, `${i}.min.json`), { encoding: 'utf-8' });
    const data = JSON.parse(json);
    data.forEach(item => {
        const { gregorian, lunar, solarTerm } = item;
        const [gan, zhi] = lunar.year;
        const lunarMonth = lunar.month.startsWith('闰') ? lunar.month.substr(1) : lunar.month;

        // data format: https://github.com/hungtcs/traditional-chinese-calendar-database/issues/3
        newData.push(
            gregorian.year - 1900,  // 公历年 8 位
            (gregorian.month << 4) + (gregorian.date >>> 1), // 月 高4位 | 日 低4位
            (gregorian.date << 7) + (TIAN_GAN.indexOf(gan) << 3) + (DI_ZHI.indexOf(zhi) >>> 1), // 日 高1位 | 天干 4 位 | 地支低 3 位
            (DI_ZHI.indexOf(zhi) << 7) + ((MONTHS.indexOf(lunarMonth) + 1) << 3) + ((DATES.indexOf(lunar.date) + 1) >>> 2), // 地支高1位 | 农历月4位 | 农历日 3 位
            ((DATES.indexOf(lunar.date) + 1) << 6) + ((lunar.leapMonth ? 1 : 0) << 5) + (JIE_QI.indexOf(solarTerm) + 1));//农历日 高2位 | 闰月 1 位 | 24 节气 5位
    });
}
fs_1.default.writeFileSync(path_1.default.join(__dirname, './all.bin'), new Uint8Array(newData), { encoding: 'binary' });

// output to c array source file.
const hexArray = Array.from(new Uint8Array(newData), byte => byte.toString(16).padStart(2, '0'));
let cArray = 'const unsigned char _lunarData[' + hexArray.length + '] = {';

for (let i = 0; i < hexArray.length; i++) {
  if (i % 16 === 0) {
    cArray += '\n  ';
  } else {
    cArray += ' ';
  }

  cArray += `0x${hexArray[i]}`;

  if (i !== hexArray.length - 1) {
    cArray += ',';
  }
}

cArray += '\n};';

fs_1.default.writeFileSync(path_1.default.join(__dirname, './all.h'), cArray, { encoding: 'utf8' });

console.log("Done!\n");
