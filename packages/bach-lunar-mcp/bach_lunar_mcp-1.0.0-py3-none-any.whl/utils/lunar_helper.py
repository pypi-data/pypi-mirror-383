"""
Lunar Python Helper / Lunar-Python封装助手

Helper functions to wrap lunar-python library for MCP tools
封装lunar-python库为MCP工具提供便利函数
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, date
import json

from lunar_python import Lunar, Solar, LunarMonth, LunarYear


class LunarHelper:
    """
    Helper class for lunar-python operations / lunar-python操作助手类
    
    Provides convenient methods for Chinese traditional calendar functions
    为中国传统历法功能提供便利方法
    """
    
    @staticmethod
    def solar_to_lunar(year: int, month: int, day: int) -> Dict[str, Any]:
        """
        Convert solar date to lunar date / 公历转农历
        
        Args:
            year: Solar year / 公历年
            month: Solar month / 公历月  
            day: Solar day / 公历日
            
        Returns:
            Dictionary containing lunar date info / 包含农历日期信息的字典
        """
        try:
            solar = Solar.fromYmd(year, month, day)
            lunar = solar.getLunar()
            
            return {
                "success": True,
                "solar_date": f"{year}-{month:02d}-{day:02d}",
                "lunar_year": lunar.getYear(),
                "lunar_month": lunar.getMonth(),
                "lunar_day": lunar.getDay(),
                "lunar_month_chinese": lunar.getMonthInChinese(),
                "lunar_day_chinese": lunar.getDayInChinese(),
                "lunar_year_chinese": lunar.getYearInChinese(),
                "lunar_date_chinese": f"{lunar.getYearInChinese()}年{lunar.getMonthInChinese()}月{lunar.getDayInChinese()}",
                "is_leap_month": lunar.getMonth() < 0,
                "zodiac": lunar.getYearShengXiao(),  # 生肖
                "gan_zhi_year": lunar.getYearInGanZhi(),  # 年干支
                "gan_zhi_month": lunar.getMonthInGanZhi(),  # 月干支
                "gan_zhi_day": lunar.getDayInGanZhi(),  # 日干支
                "jie_qi": lunar.getJieQi(),  # 节气
                "week_chinese": solar.getWeekInChinese(),
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error converting date / 日期转换错误: {str(e)}"
            }
    
    @staticmethod
    def lunar_to_solar(lunar_year: int, lunar_month: int, lunar_day: int, 
                      is_leap: bool = False) -> Dict[str, Any]:
        """
        Convert lunar date to solar date / 农历转公历
        
        Args:
            lunar_year: Lunar year / 农历年
            lunar_month: Lunar month / 农历月
            lunar_day: Lunar day / 农历日
            is_leap: Is leap month / 是否闰月
            
        Returns:
            Dictionary containing solar date info / 包含公历日期信息的字典
        """
        try:
            lunar = Lunar.fromYmd(lunar_year, lunar_month, lunar_day)
            if is_leap:
                lunar = Lunar.fromYmd(lunar_year, -lunar_month, lunar_day)
                
            solar = lunar.getSolar()
            
            return {
                "success": True,
                "lunar_date": f"{lunar_year}-{lunar_month:02d}-{lunar_day:02d}",
                "solar_year": solar.getYear(),
                "solar_month": solar.getMonth(),
                "solar_day": solar.getDay(),
                "solar_date": f"{solar.getYear()}-{solar.getMonth():02d}-{solar.getDay():02d}",
                "week_chinese": solar.getWeekInChinese(),
                "is_leap_month": is_leap
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error converting lunar date / 农历日期转换错误: {str(e)}"
            }
    
    @staticmethod
    def get_bazi(year: int, month: int, day: int, hour: int, minute: int = 0) -> Dict[str, Any]:
        """
        Calculate BaZi (Eight Characters) / 计算生辰八字
        
        Args:
            year: Birth year / 出生年
            month: Birth month / 出生月
            day: Birth day / 出生日
            hour: Birth hour / 出生时
            minute: Birth minute / 出生分钟
            
        Returns:
            Dictionary containing BaZi info / 包含八字信息的字典
        """
        try:
            solar = Solar.fromYmdHms(year, month, day, hour, minute, 0)
            lunar = solar.getLunar()
            
            # Get eight characters / 获取八字
            bazi = lunar.getEightChar()
            
            # Get individual components / 获取各个组成部分
            year_gan_zhi = f"{bazi.getYearGan()}{bazi.getYearZhi()}"
            month_gan_zhi = f"{bazi.getMonthGan()}{bazi.getMonthZhi()}"
            day_gan_zhi = f"{bazi.getDayGan()}{bazi.getDayZhi()}"
            time_gan_zhi = f"{bazi.getTimeGan()}{bazi.getTimeZhi()}"
            
            return {
                "success": True,
                "birth_datetime": f"{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}",
                "year_gan_zhi": year_gan_zhi,  # 年柱
                "month_gan_zhi": month_gan_zhi,  # 月柱
                "day_gan_zhi": day_gan_zhi,  # 日柱
                "hour_gan_zhi": time_gan_zhi,  # 时柱
                "bazi_string": f"{year_gan_zhi} {month_gan_zhi} {day_gan_zhi} {time_gan_zhi}",
                "zodiac": lunar.getYearShengXiao(),  # 生肖
                "wu_xing": {  # 五行
                    "year": bazi.getYearWuXing(),
                    "month": bazi.getMonthWuXing(), 
                    "day": bazi.getDayWuXing(),
                    "hour": bazi.getTimeWuXing()
                },
                "na_yin": {  # 纳音
                    "year": bazi.getYearNaYin(),
                    "month": bazi.getMonthNaYin(),
                    "day": bazi.getDayNaYin(),
                    "hour": bazi.getTimeNaYin()
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error calculating BaZi / 八字计算错误: {str(e)}"
            }
    
    @staticmethod
    def get_huangli(year: int, month: int, day: int) -> Dict[str, Any]:
        """
        Get Huangli (Chinese Almanac) info / 获取黄历信息
        
        Args:
            year: Year / 年
            month: Month / 月
            day: Day / 日
            
        Returns:
            Dictionary containing almanac info / 包含黄历信息的字典
        """
        try:
            solar = Solar.fromYmd(year, month, day)
            lunar = solar.getLunar()
            
            return {
                "success": True,
                "date": f"{year}-{month:02d}-{day:02d}",
                "lunar_date_chinese": f"{lunar.getYearInChinese()}年{lunar.getMonthInChinese()}月{lunar.getDayInChinese()}",
                "gan_zhi_year": lunar.getYearInGanZhi(),
                "gan_zhi_month": lunar.getMonthInGanZhi(),
                "gan_zhi_day": lunar.getDayInGanZhi(),
                "zodiac": lunar.getYearShengXiao(),
                "jie_qi": lunar.getJieQi(),  # 节气
                "yi": lunar.getDayYi(),  # 宜
                "ji": lunar.getDayJi(),  # 忌
                "shen_sha": lunar.getDayShengXiao(),  # 神煞
                "chong": lunar.getDayChong(),  # 冲
                "sha": lunar.getDaySha(),  # 煞
                "wu_xing": f"{lunar.getDayGan()}{lunar.getDayZhi()}",  # 五行 - 使用干支表示
                "pengzu_gan": lunar.getPengZuGan(),  # 彭祖百忌天干
                "pengzu_zhi": lunar.getPengZuZhi(),  # 彭祖百忌地支
                "week_chinese": solar.getWeekInChinese(),
                "festivals": solar.getFestivals() + lunar.getFestivals(),  # 节日
                "other_festivals": solar.getOtherFestivals() + lunar.getOtherFestivals()  # 其他节日
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error getting Huangli / 黄历获取错误: {str(e)}"
            }
    
    @staticmethod
    def get_jie_qi_list(year: int) -> Dict[str, Any]:
        """
        Get list of Jie Qi (24 Solar Terms) for a year / 获取一年的节气列表
        
        Args:
            year: Year / 年份
            
        Returns:
            Dictionary containing Jie Qi list / 包含节气列表的字典
        """
        try:
            jie_qi_list = []
            
            # Get all months in the year / 获取一年中的所有月份
            for month in range(1, 13):
                # Get first day of each month / 获取每月第一天
                solar = Solar.fromYmd(year, month, 1)
                lunar = solar.getLunar()
                
                # Get Jie Qi for this month / 获取本月节气
                jie_qi = lunar.getJieQi()
                if jie_qi:
                    jie_qi_list.append({
                        "name": jie_qi,
                        "month": month,
                        "solar_date": f"{year}-{month:02d}-01"
                    })
            
            return {
                "success": True,
                "year": year,
                "jie_qi_list": jie_qi_list,
                "total_count": len(jie_qi_list)
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error getting Jie Qi list / 节气列表获取错误: {str(e)}"
            }
    
    @staticmethod
    def analyze_wu_xing(year: int, month: int, day: int, hour: int, minute: int = 0) -> Dict[str, Any]:
        """
        Analyze Wu Xing (Five Elements) / 分析五行
        
        Args:
            year: Birth year / 出生年
            month: Birth month / 出生月
            day: Birth day / 出生日
            hour: Birth hour / 出生时
            minute: Birth minute / 出生分钟
            
        Returns:
            Dictionary containing Wu Xing analysis / 包含五行分析的字典
        """
        try:
            solar = Solar.fromYmdHms(year, month, day, hour, minute, 0)
            lunar = solar.getLunar()
            bazi = lunar.getEightChar()
            
            # Count Wu Xing elements / 统计五行元素
            wu_xing_count = {"金": 0, "木": 0, "水": 0, "火": 0, "土": 0}
            
            elements = [
                bazi.getYearWuXing(),
                bazi.getMonthWuXing(),
                bazi.getDayWuXing(),
                bazi.getTimeWuXing()
            ]
            
            # Each element string may contain multiple characters like "火水"
            # We need to count each individual element / 每个元素字符串可能包含多个字符如"火水"，需要单独统计
            for element_str in elements:
                if element_str:
                    for char in element_str:
                        if char in wu_xing_count:
                            wu_xing_count[char] += 1
            
            # Find dominant and missing elements / 找出旺相和缺失的元素
            max_count = max(wu_xing_count.values())
            min_count = min(wu_xing_count.values())
            
            dominant_elements = [k for k, v in wu_xing_count.items() if v == max_count]
            missing_elements = [k for k, v in wu_xing_count.items() if v == 0]
            weak_elements = [k for k, v in wu_xing_count.items() if v == min_count and v > 0]
            
            return {
                "success": True,
                "birth_datetime": f"{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}",
                "wu_xing_count": wu_xing_count,
                "dominant_elements": dominant_elements,  # 旺相元素
                "missing_elements": missing_elements,   # 缺失元素
                "weak_elements": weak_elements,         # 偏弱元素
                "bazi_wu_xing": {
                    "year": bazi.getYearWuXing(),
                    "month": bazi.getMonthWuXing(),
                    "day": bazi.getDayWuXing(),
                    "hour": bazi.getTimeWuXing()
                },
                "analysis_summary": f"五行统计: {wu_xing_count}, 旺: {dominant_elements}, 缺: {missing_elements}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error analyzing Wu Xing / 五行分析错误: {str(e)}"
            }
