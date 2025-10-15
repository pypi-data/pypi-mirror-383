/*
 * (C) Copyright 2023, Eumetnet
 *
 * This file is part of the E-SOH Norbufr BUFR en/decoder interface
 *
 * Author: istvans@met.no
 *
 */

#ifndef _ESOHBUFR_
#define _ESOHBUFR_

#include <list>
#include <map>
#include <sstream>
#include <string>

#include "rapidjson/document.h"
#include "rapidjson/prettywriter.h"

#include "NorBufr.h"
#include "Oscar.h"
#include "WSI.h"

// Default BUFR-CF map
static std::map<DescriptorId, std::pair<std::string, std::string>> cf_names = {
    {DescriptorId(10004, true), {"air_pressure", "Pa"}},
    {DescriptorId(10051, true), {"air_pressure_at_mean_sea_level", "Pa"}},

    {DescriptorId(11001, true), {"wind_from_direction", "degree"}},
    {DescriptorId(11002, true), {"wind_speed", "m s-1"}},
    {DescriptorId(11043, true), {"wind_gust_from_direction", "degree"}},
    {DescriptorId(11041, true), {"wind_speed_of_gust", "m s-1"}},

    {DescriptorId(12001, true), {"air_temperature", "K"}},
    {DescriptorId(12004, true), {"air_temperature", "K"}},
    {DescriptorId(12101, true), {"air_temperature", "K"}},
    {DescriptorId(12104, true), {"air_temperature", "K"}},
    {DescriptorId(12003, true), {"dew_point_temperature", "K"}},
    {DescriptorId(12006, true), {"dew_point_temperature", "K"}},
    {DescriptorId(12103, true), {"dew_point_temperature", "K"}},
    {DescriptorId(12106, true), {"dew_point_temperature", "K"}},

    {DescriptorId(13003, true), {"relative_humidity", "%"}},

    {DescriptorId(13011, true), {"precipitation_amount", "kg m-2"}},
    {DescriptorId(13023, true), {"precipitation_amount", "kg m-2"}},

    {DescriptorId(20001, true), {"visibility_in_air", "m"}},

    {DescriptorId(14002, true),
     {"integral_wrt_time_of_surface_downwelling_longwave_flux_in_air",
      "W s m-2"}},
    {DescriptorId(14004, true),
     {"integral_wrt_time_of_surface_downwelling_shortwave_flux_in_air",
      "W s m-2"}},
    {DescriptorId(14012, true),
     {"integral_wrt_time_of_surface_net_downward_longwave_flux", "W s m-2"}},
    {DescriptorId(14013, true),
     {"integral_wrt_time_of_surface_net_downward_shortwave_flux", "W s m-2"}},

    {DescriptorId(22042, true), {"sea_water_temperature", "K"}},
    {DescriptorId(22043, true), {"sea_water_temperature", "K"}},
    {DescriptorId(22045, true), {"sea_water_temperature", "K"}},

    {DescriptorId(25006, true), {"radar_estimated_precipitation_rate", "mm/h"}},
    {DescriptorId(321008, true),
     {"radar_equivalent_reflectivity_factor_h", "dBz"}}};

static std::string default_shadow_wigos("0-0-0-");

static std::list<std::pair<char, char>> repl_chars = {
    {' ', '_'}, {'-', '_'}, {'\'', '_'}};

class ESOHBufr : public NorBufr {

public:
  ESOHBufr();
  std::list<std::string> msg() const;
  void setOscar(Oscar *);
  void setMsgTemplate(std::string);
  bool setShadowWigos(std::string);
  void setShadowWigos(const WSI &wsi);
  void setRadarCFMap(std::map<std::string, std::string> &);

private:
  std::string addMessage(std::list<Descriptor>::const_iterator ci,
                         rapidjson::Document &message, char sensor_level_active,
                         double sensor_level, std::string fn = "",
                         time_t *start_datetime = 0,
                         std::string period_str = "", std::string force_cf = "",
                         std::string force_value = "") const;
  bool addDescriptor(Descriptor &D, rapidjson::Value &dest,
                     rapidjson::Document::AllocatorType &) const;
  bool addContent(const Descriptor &D, std::string cf_name,
                  char sensor_level_active, double sensor_level, std::string fn,
                  rapidjson::Document &, std::string force_value = "") const;
  bool setPlatformName(std::string v, rapidjson::Document &message,
                       bool force = true) const;
  bool setPlatform(std::string v, rapidjson::Document &message) const;
  bool setRadarMeta(std::string v, rapidjson::Document &message) const;
  bool setLocation(double lat, double lon, double hei,
                   rapidjson::Document &) const;
  bool updateLocation(double loc, std::string loc_label,
                      rapidjson::Document &message) const;

  bool setDateTime(struct tm *, rapidjson::Document &,
                   std::string period_str = "") const;
  bool setStartDateTime(struct tm *, rapidjson::Document &,
                        std::string period_str = "") const;
  WSI genShadowWigosId(std::list<Descriptor> &,
                       std::list<Descriptor>::const_iterator &cir) const;
  void initTimeInterval();
  bool timeInInterval(time_t t) const;
  bool timeInInterval(struct tm) const;

  Oscar *oscar;
  std::string msg_template;
  WSI shadow_wigos;
  bool dynamictime = true;
  int64_t lotime = 86400;
  int64_t hitime = -600;
  std::map<std::string, std::string> radar_cf_map;
};

int64_t getTimeStamp(const char *env_time);
uint64_t periodStrToSec(std::string p_str);

#if defined(_MSC_VER)
// light implementation of strptime, for win build
// one format is supported: "%Y-%m-%dT%H:%M:%SZ"
char *strptime_esoh(const char *s, const char *format, struct tm *tm);
#endif

#endif
