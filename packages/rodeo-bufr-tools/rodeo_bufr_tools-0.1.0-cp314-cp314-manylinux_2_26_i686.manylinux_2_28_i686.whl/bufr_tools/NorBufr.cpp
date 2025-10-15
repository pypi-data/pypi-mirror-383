/*
 * (C) Copyright 2023, met.no
 *
 * This file is part of the Norbufr BUFR en/decoder
 *
 * Author: istvans@met.no
 *
 */

#include <algorithm>
#include <bitset>
#include <cmath>
#include <iomanip>
#include <limits>
#include <sstream>
#include <stack>
#include <string.h>
#include <string>

#include "NorBufr.h"
#include "NorBufrIO.h"

NorBufr::NorBufr() {
  buffer = 0;
  // tabA = 0;
  tabB = 0;
  tabC = 0;
  tabD = 0;

  len = 0;
  edition = 4;
  lb.setLogLevel(norbufr_default_loglevel);
}

NorBufr::~NorBufr() {
  if (buffer)
    delete[] buffer;
  // clearTable();
  for (auto v : extraMeta)
    delete v;
  extraMeta.clear();
}

void NorBufr::setTableDir(std::string s) {
  table_dir = s;

  // TODO: add ecctables
  // TableA * ta = new TableA(table_dir + "BUFRCREX_TableA_en.txt");
  // tabA = ta;
  TableB *tb = new TableB(table_dir + "/BUFRCREX_TableB_en.txt");
  tabB = tb;
  TableC *tc = new TableC(table_dir + "/BUFRCREX_CodeFlag_en.txt");
  tabC = tc;
  TableD *td = new TableD(table_dir + "/BUFR_TableD_en.txt");
  tabD = td;
}

uint64_t NorBufr::uncompressDescriptor(std::list<DescriptorId>::iterator &it,
                                       ssize_t &sb, ssize_t &subsetsb,
                                       uint32_t *repeatnum) {

  lb.addLogEntry(LogEntry("Starting Descriptor uncompressing", LogLevel::DEBUG,
                          __func__, bufr_id));
  uint64_t repeat0 = 0;
  DescriptorMeta dm = tabB->at(*it);
  ssize_t referenceNull =
      NorBufrIO::getBitValue(sb, tabB->at(*it).datawidth(), false, bits);
  sb += tabB->at(*it).datawidth();
  ssize_t NBINC = NorBufrIO::getBitValue(sb, 6, false, bits);
  sb += 6;
  for (uint32_t s = 0; s < subsets.size(); ++s) {
    ssize_t increment = NorBufrIO::getBitValue(sb, NBINC, true, bits);
    // if delayed, don't push_back
    if (s || !repeatnum)
      desc[s].push_back(Descriptor(*it, subsetsb));
    Descriptor &current_desc = desc[s].back();

    if (tabB->at(*it).unit().find("CCITTIA5") != std::string::npos) {
      std::vector<bool> bl;
      if (NBINC) {
        std::string bs;
        bs = NorBufrIO::getBitStr(sb, NBINC * 8, bits);

        bl = NorBufrIO::getBitVec(sb, NBINC * 8, bits);
        ucbits.insert(ucbits.end(), bl.begin(), bl.end());
      }
      int bitdiff = dm.datawidth() - NBINC * 8;
      if (bitdiff) {
        DescriptorMeta *dmn = new DescriptorMeta;
        *dmn = dm;
        dmn->setDatawidth(bl.size());
        auto dm_ptr = addMeta(dmn);
        // Meta already exists
        if (dm_ptr != dmn)
          delete dmn;
        current_desc.setMeta(dm_ptr);
      } else {
        current_desc.setMeta(const_cast<DescriptorMeta *>(&(tabB->at(*it))));
        current_desc.setStartBit(subsetsb);
      }

      subsetsb += NBINC * 8;
      sb += NBINC * 8;

    } else {
      // TODO:assoc_field !!!

      uint64_t val;

      if (increment == (std::numeric_limits<ssize_t>::max)())
        val = (std::numeric_limits<uint64_t>::max)();
      else
        val = referenceNull + increment;

      if (repeatnum) {
        if (!s)
          repeat0 = val;
        else {
          if (repeat0 != val) {
            lb.addLogEntry(LogEntry("Compressed delayed descriptor error!" +
                                        std::to_string(repeat0) + " [" +
                                        std::to_string(val) + "]",
                                    LogLevel::FATAL, __func__, bufr_id));
            // TODO: clean
          }
        }
        *repeatnum = val;
      }

      std::vector<bool> bl = NorBufrIO::valueToBitVec(val, dm.datawidth());

      ucbits.insert(ucbits.end(), bl.begin(), bl.end());

      current_desc.setStartBit(subsetsb);
      current_desc.setMeta(const_cast<DescriptorMeta *>(&(tabB->at(*it))));

      subsetsb += dm.datawidth();
      sb += NBINC;
    }
  }

  return 0;
}

ssize_t NorBufr::extractDescriptors(int ss, ssize_t subsb) {

  lb.addLogEntry(
      LogEntry("Starting extract Descriptors, subset: " + std::to_string(ss),
               LogLevel::DEBUG, __func__, bufr_id));

  if (!subsetNum() || !(sec3_desc.size()))
    return 0;

  ssize_t sb = subsb; // startbit
  // subset startbit
  ssize_t subsetsb = 0;
  ssize_t mod_datawidth = 0;
  ssize_t mod_str_datawidth = 0;
  ssize_t local_datawidth = 0;
  int mod_scale = 0;
  int mod_refvalue_mul = 0;
  std::map<DescriptorId, int> mod_refvalue;

  std::stack<uint8_t> assoc_field;

  std::list<DescriptorId> DL = sec3_desc;

  for (auto it = DL.begin(); it != DL.end(); ++it) {
    if (isCompressed()) {
      if (sb >= static_cast<ssize_t>(bits.size())) {
        std::stringstream ss;
        ss << "Compressed Section4 size error!!! " << sb << "["
           << static_cast<ssize_t>(bits.size()) << "] ";
        ss << "Compressed: " << isCompressed() << " ";
        ss << "IT: " << std::dec << *it << " ";
        ss << "Subset: " << subsetNum();
        lb.addLogEntry(LogEntry(ss.str(), LogLevel::ERROR_, __func__, bufr_id));
        return sb;
      }
    }

    lb.addLogEntry(LogEntry("Descriptor extract:" + it->toString(),
                            LogLevel::TRACE, __func__, bufr_id));
    switch (it->f()) {
    case 0: // Element Descriptor
    {
      if (isCompressed()) {
        uncompressDescriptor(it, sb, subsetsb);
      } else {
        if (!assoc_field.empty() && (it->x() != 31 && it->y() != 21))
          sb += assoc_field.top();

        desc[ss].push_back(Descriptor(*it, sb));

        Descriptor &current_desc = desc[ss].back();

        // local Descriptor, datawidth definef by previous descriptor [ 2 06 YYY
        // ]
        if (local_datawidth) {
          DescriptorMeta *dm = new DescriptorMeta;
          *dm = tabB->at(*it);
          dm->setDatawidth(local_datawidth);
          auto dm_ptr = addMeta(dm);
          // Meta already exists
          if (dm_ptr != dm)
            delete dm;
          current_desc.setMeta(dm_ptr);
          sb += local_datawidth;
          local_datawidth = 0;
          break;
        }

        if (tabB->at(*it).unit().find("CCITTIA5") != std::string::npos) {
          if (mod_str_datawidth) {
            sb += mod_str_datawidth;
            DescriptorMeta *dm = new DescriptorMeta;
            *dm = tabB->at(*it);
            if (mod_str_datawidth)
              dm->setDatawidth(mod_str_datawidth);
            auto dm_ptr = addMeta(dm);
            // Meta already exists
            if (dm_ptr != dm)
              delete dm;
            current_desc.setMeta(dm_ptr);
          } else {
            sb += tabB->at(*it).datawidth();
            current_desc.setMeta(
                const_cast<DescriptorMeta *>(&(tabB->at(*it))));
          }
        } else {
          if (tabB->at(*it).unit().find("CODE TABLE") != std::string::npos ||
              tabB->at(*it).unit().find("FLAG TABLE") != std::string::npos) {
            sb += tabB->at(*it).datawidth();
            current_desc.setMeta(
                const_cast<DescriptorMeta *>(&(tabB->at(*it))));
          } else {
            sb += tabB->at(*it).datawidth() + mod_datawidth;

            if (sb > static_cast<ssize_t>(bits.size())) {
              // TODO: set missing ???
              std::stringstream ss;
              ss << "Section4 size error!!! " << sb << "["
                 << static_cast<ssize_t>(bits.size()) << "] ";
              ss << "Compressed: " << isCompressed() << " ";
              ss << "IT: " << std::dec << *it << " ";
              ss << "Subset: " << subsetNum();
              lb.addLogEntry(
                  LogEntry(ss.str(), LogLevel::ERROR_, __func__, bufr_id));
              return sb;
            }

            if ((!mod_scale && !mod_refvalue_mul &&
                 (mod_refvalue.find(*it) == mod_refvalue.end()) &&
                 !mod_datawidth && assoc_field.empty()) ||
                (it->x() == 31 && it->y() == 21)) {
              // TODO: Too ugly !!
              current_desc.setMeta(
                  const_cast<DescriptorMeta *>(&(tabB->at(*it))));
            } else {

              DescriptorMeta *dm = new DescriptorMeta;
              *dm = tabB->at(*it);
              if (!assoc_field.empty()) {
                dm->setAssocwidth(assoc_field.top());
              }
              if (mod_datawidth)
                dm->setDatawidth(dm->datawidth() + mod_datawidth);
              if (mod_scale)
                dm->setScale(dm->scale() + mod_scale);

              int mref = dm->reference();
              if (mod_refvalue.find(*it) != mod_refvalue.end()) {
                mref = mod_refvalue[*it];
              }
              if (mod_refvalue_mul)
                mref *= mod_refvalue_mul;
              dm->setReference(mref);

              auto dm_ptr = addMeta(dm);
              // Meta already exists
              if (dm_ptr != dm)
                delete dm;
              current_desc.setMeta(dm_ptr);
            }
          }
        }
      }
      break;
    }
    case 1: // Replication Descriptors
    {
      desc[ss].push_back(Descriptor(*it, sb));
      uint64_t index = 0;
      int descnum = it->x();
      uint32_t repeatnum = 0;
      if (it->y() != 0)
        repeatnum = it->y();
      else {
        // Delayed descriptor [ 0 31 YYY ]
        ++it;
        if (it == DL.end()) {
          lb.addLogEntry(LogEntry("Delayed descriptor missing!",
                                  LogLevel::ERROR_, __func__, bufr_id));
        }
        desc[ss].push_back(Descriptor(*it, sb));
        if (it->f() == 0 && it->x() == 31) {
          if (!isCompressed()) {
            if (sb <=
                static_cast<ssize_t>(bits.size() - tabB->at(*it).datawidth())) {
              repeatnum = NorBufrIO::getBitValue(sb, tabB->at(*it).datawidth(),
                                                 false, bits);
              index += tabB->at(*it).datawidth();
              Descriptor &cd = desc[ss].back();
              cd.setMeta(const_cast<DescriptorMeta *>(&(tabB->at(*it))));
            } else {
              lb.addLogEntry(LogEntry("REPEAT 0      2 ---->> ",
                                      LogLevel::ERROR_, __func__, bufr_id));
              repeatnum = 0;
            }
          } else {
            uncompressDescriptor(it, sb, subsetsb, &repeatnum);
          }
        } else {
          lb.addLogEntry(
              LogEntry("Delayed Descriprtor error: " + it->toString(),
                       LogLevel::ERROR_, __func__, bufr_id));
        }
      }

      std::list<DescriptorId> repeat_descriptors;
      auto rep_it = it;
      for (int i = 0; i < descnum; ++i) {
        if (++rep_it != DL.end()) {
          DescriptorId d = *(rep_it);
          if (repeatnum) {
            repeat_descriptors.push_back(d);
          } else {
            ++it;
          }
        } else {
          if (repeatnum)
            lb.addLogEntry(LogEntry("Missing descriptors: " +
                                        std::to_string(descnum - 1 - i),
                                    LogLevel::ERROR_, __func__, bufr_id));
          break;
        }
      }
      if (repeatnum) {
        auto insert_here = ++rep_it;
        for (uint32_t i = 1; i < repeatnum; ++i)
          DL.insert(insert_here, repeat_descriptors.begin(),
                    repeat_descriptors.end());
      }

      sb += index;
      break;
    }
    case 2: // Operator Descriptors
    {
      desc[ss].push_back(Descriptor(*it, sb));
      if (isCompressed())
        break;

      switch (it->x()) {
      case 1:
        if (it->y())
          mod_datawidth = it->y() - 128;
        else
          mod_datawidth = 0;
        break;
      case 2:
        if (it->y())
          mod_scale = it->y() - 128;
        else
          mod_scale = 0;
        break;
      case 3: {
        if (it->y() != 255 && it->y()) {
          int64_t nref = 0;
          uint64_t nextbit = it->y();
          uint64_t bitref = NorBufrIO::getBitValue(sb, it->y(), false, bits);
          if (bitref != ULONG_MAX) {
            uint64_t sign = NorBufrIO::getBitValue(sb, 1, false, bits);
            if (sign) {
              bitref = NorBufrIO::getBitValue(sb + 1, it->y() - 1, false, bits);
              nref = -bitref;
            } else
              nref = bitref;
            ++it;
            while (*it != DescriptorId("203255") && it != DL.end()) {
              desc[ss].push_back(Descriptor(*it, sb));
              Descriptor &current_desc = desc[ss].back();

              DescriptorMeta *dm = new DescriptorMeta;
              *dm = tabB->at(*it);
              dm->setDatawidth(0);
              std::string orig_name = dm->name();
              dm->setName("New Reference Value [" + orig_name +
                          "]:" + std::to_string(nref));
              dm->setUnit("Reference");
              auto dm_ptr = addMeta(dm);
              // Meta already exists
              if (dm_ptr != dm)
                delete dm;
              current_desc.setMeta(dm_ptr);
              mod_refvalue[*it] = nref;
              ++it;
            }
          }
          sb += nextbit;
        } else {
          mod_refvalue.clear();
        }
        break;
      }
      case 4: {
        if (it->y() != 000) {
          if (assoc_field.empty())
            assoc_field.push(it->y());
          else
            assoc_field.push(it->y() + assoc_field.top());
        } else {
          assoc_field.pop();
        }
        break;
      }
      case 5:
        sb += it->y() * 8;
        break;
      case 6:
        local_datawidth = it->y();
        break;
      case 7: {
        if (it->y() == 0) {
          mod_scale = 0;
          mod_refvalue_mul = 0;
          mod_datawidth = 0;
        } else {
          mod_scale = it->y();
          mod_refvalue_mul = pow(10, it->y());
          mod_datawidth = (int)((10 * it->y() + 2) / 3);
        }
        break;
      }
      case 8:
        mod_str_datawidth = it->y() * 8;
        break;

      default:
        lb.addLogEntry(LogEntry("Not yet implemented: " + it->toString(),
                                LogLevel::ERROR_, __func__, bufr_id));
      }

      break;
    }
    case 3: // Sequence Descriptors
    {
      desc[ss].push_back(Descriptor(*it, sb));
      auto dl = tabD->expandDescriptor(*it);
      auto ih = it;
      dl.splice(++ih, dl);
      break;
    }

    default: {

      break;
    }
    }
  }

  lb.addLogEntry(LogEntry("End Descriptors, endbit: " + std::to_string(sb),
                          LogLevel::DEBUG, __func__, bufr_id));

  // Create SUBSETS
  ssize_t endbit = sb;
  if (!subsb)
    subsets.at(0) = 0;

  // [0 31 XXX] is different in each subset
  if (!isCompressed()) {
    if (!subsb) {
      if (subsets.size() > 1) {
        for (uint32_t i = 1; i < subsets.size(); ++i) {
          subsets.at(i) = endbit;
          endbit = extractDescriptors(i, endbit);
        }
      }
    }
  }

  return endbit;
}

void NorBufr::clearTable() {
  //    if ( tabA ) delete tabA;
  if (tabB)
    delete tabB;
  if (tabC)
    delete tabC;
  if (tabD)
    delete tabD;
}

void NorBufr::clear() {
  Section2::clear();
  Section3::clear();
  Section4::clear();
  freeBuffer();
  desc.clear();
  subsets.clear();
  for (auto v : extraMeta)
    delete v;
  extraMeta.clear();
  ucbits.clear();
  edition = 0;
  lb.clear();
}

void NorBufr::freeBuffer() {
  if (buffer)
    delete[] buffer;
  buffer = 0;
  len = 0;
}

uint64_t NorBufr::length() const { return len; }

bool NorBufr::saveBuffer(std::string filename) const {
  std::ofstream os(filename, std::ifstream::binary);
  os.write(reinterpret_cast<char *>(buffer), len);
  os.close();
  return os.good();
}

std::vector<DescriptorMeta *>::iterator NorBufr::findMeta(DescriptorMeta *dm) {
  auto it = extraMeta.begin();
  for (; it != extraMeta.end(); ++it) {
    if (**it == *dm) {
      return it;
    }
  }

  return extraMeta.end();
}

DescriptorMeta *NorBufr::addMeta(DescriptorMeta *dm) {
  auto it = findMeta(dm);
  if (it == extraMeta.end()) {
    extraMeta.push_back(dm);
    return extraMeta.back();
  } else {
    return *it;
  }
}

double NorBufr::getValue(const Descriptor &d, double) const {
  const DescriptorMeta *dm = d.getMeta();
  double dvalue = std::numeric_limits<double>::quiet_NaN();

  if (dm) {
    const std::vector<bool> &bitref = (isCompressed() ? ucbits : bits);
    uint64_t raw_value = NorBufrIO::getBitValue(
        d.startBit(), dm->datawidth(), !(d.f() == 0 && d.x() == 31), bitref);

    if (raw_value == (std::numeric_limits<uint64_t>::max)())
      return (dvalue);

    dvalue = static_cast<double>(raw_value);
    if (dm->reference())
      dvalue += dm->reference();
    if (dm->scale()) {
      dvalue = dvalue / pow(10.0, dm->scale());
    }
  }

  return dvalue;
}

uint64_t NorBufr::getBitValue(const Descriptor &d, uint64_t) const {
  const DescriptorMeta *dm = d.getMeta();
  uint64_t value = 0;

  if (dm) {
    const std::vector<bool> &bitref = (isCompressed() ? ucbits : bits);
    value = NorBufrIO::getBitValue(d.startBit(), dm->datawidth(),
                                   !(d.f() == 0 && d.x() == 31), bitref);

    if (value == (std::numeric_limits<uint64_t>::max)())
      return (value);
  }

  return value;
}

int NorBufr::getValue(const Descriptor &d, int) const {
  const DescriptorMeta *dm = d.getMeta();
  int value = (std::numeric_limits<int>::max)();

  if (dm) {
    const std::vector<bool> &bitref = (isCompressed() ? ucbits : bits);
    uint64_t raw_value = NorBufrIO::getBitValue(
        d.startBit(), dm->datawidth(), !(d.f() == 0 && d.x() == 31), bitref);
    if (raw_value == (std::numeric_limits<uint64_t>::max)())
      return (value);
    value = static_cast<int>(raw_value);
    if (dm->reference())
      value += dm->reference();
    if (dm->scale()) {
      value = value / pow(10.0, dm->scale());
    }
  }

  return value;
}

std::string NorBufr::getValue(const Descriptor &d, std::string,
                              bool with_unit) const {
  std::string ret;
  const DescriptorMeta *dm = d.getMeta();

  if (dm) {
    const std::vector<bool> &bitref = (isCompressed() ? ucbits : bits);
    // String
    if ((d.f() == 2 && d.x() == 5) ||
        dm->unit().find("CCITTIA5") != std::string::npos) {
      bool missing = true;
      for (uint16_t i = 0; i < dm->datawidth(); i += 8) {
        uint64_t c = NorBufrIO::getBitValue(d.startBit() + i, 8, true, bitref);
        if (c)
          ret += static_cast<char>(c);
        if ((std::numeric_limits<uint64_t>::max)() != c)
          missing = false;
      }
      if (missing)
        ret = "MISSING";
      return ret;
    }

    uint64_t raw_value = NorBufrIO::getBitValue(
        d.startBit(), dm->datawidth(), !(d.f() == 0 && d.x() == 31), bitref);

    if (raw_value == (std::numeric_limits<uint64_t>::max)())
      return ("MISSING");

    if (d.f() == 0 && d.x() == 31)
      return std::to_string(raw_value);

    if (!dm->reference() &&
        (dm->unit().find("CODE TABLE") != std::string::npos ||
         dm->unit().find("FLAG TABLE") != std::string::npos)) {
      std::stringstream ss(tabB->at(d).unit());

      ret = (tabC) ? tabC->codeStr(d, raw_value) : "?";
    } else {
      double dvalue = raw_value;
      if (dm->reference())
        dvalue += dm->reference();
      if (dm->scale()) {
        dvalue = dvalue / pow(10.0, dm->scale());
      }
      std::stringstream ss;
      if (d.x() == 1) {
        ss << std::fixed << std::setprecision(0);
      }
      ss << dvalue;
      ret = ss.str();
      if (with_unit)
        ret += " " + dm->unit();
    }
  }
  return ret;
}

uint64_t NorBufr::fromBuffer(char *ext_buf, uint64_t ext_buf_pos,
                             uint64_t ext_buf_size) {
  clear();
  if (buffer) {
    delete[] buffer;
    buffer = 0;
  }

  lb.addLogEntry(
      LogEntry("Reading >> BUFR at position: " + std::to_string(ext_buf_pos),
               LogLevel::DEBUG, __func__, bufr_id));

  // Search "BUFR" string
  unsigned long n = NorBufrIO::findBytes(ext_buf + ext_buf_pos,
                                         ext_buf_size - ext_buf_pos, "BUFR", 4);
  if (n >= ext_buf_size) {
    lb.addLogEntry(
        LogEntry("No more BUFR messages", LogLevel::INFO, __func__, bufr_id));
    return n;
  }

  // Section0 length
  const uint64_t slen = 8;
  uint8_t sec0[slen];
  if (ext_buf_pos + n + slen < ext_buf_size) {
    memcpy(sec0, ext_buf + ext_buf_pos + n, slen);
  }

  len = NorBufrIO::getBytes(sec0 + 4, 3);
  edition = sec0[7];

  lb.addLogEntry(LogEntry("BUFR Size: " + std::to_string(len) +
                              " Edition: " + std::to_string(edition),
                          LogLevel::DEBUG, __func__, bufr_id));

  buffer = new uint8_t[len];
  memcpy(buffer, sec0, slen);

  if (ext_buf_pos + n + len <= ext_buf_size) {
    memcpy(buffer + slen, ext_buf + ext_buf_pos + n + slen, len - slen);
  }

  int offset = checkBuffer();
  if (offset) {
    lb.addLogEntry(LogEntry("Offset: " + std::to_string(offset),
                            LogLevel::DEBUG, __func__, bufr_id));
  }
  setSections(slen);

  return ext_buf_pos + len;
}

const uint8_t *NorBufr::toBuffer() {
  size_t total_length = 12; // "BUFR" + Section0 + "7777"

  total_length += Section1::length();

  if (getOptionalSelection())
    total_length += Section2::length();
  total_length += Section3::length() + Section4::length();

  uint8_t *retbuf = new uint8_t[total_length];
  memset(retbuf, 0, total_length);
  size_t bufpos = 0;

  memcpy(reinterpret_cast<char *>(retbuf), "BUFR", 4);
  NorBufrIO::setBytes(retbuf + 4, len, 3);
  NorBufrIO::setBytes(retbuf + 7, edition, 1);

  bufpos += 8;
  Section1::toBuffer(retbuf + bufpos);
  bufpos += Section1::len;
  if (Section1::getOptionalSelection()) {
    Section2::toBuffer(retbuf + bufpos);
    bufpos += Section2::len;
  }

  Section3::toBuffer(retbuf + bufpos);
  bufpos += Section3::len;
  Section4::toBuffer(retbuf + bufpos);
  bufpos += Section4::len;

  memcpy(retbuf + bufpos, "7777", 4);
  NorBufr::len = total_length;
  return retbuf;
  // TODO: buffer -> retbuf;
  // return buffer;
}

std::istream &operator>>(std::istream &is, NorBufr &bufr) {
  bufr.clear();
  if (bufr.buffer) {
    delete[] bufr.buffer;
    bufr.buffer = 0;
  }

  bufr.lb.addLogEntry(
      LogEntry("Reading >> BUFR at position: " + std::to_string(is.tellg()),
               LogLevel::DEBUG, __func__, bufr.bufr_id));

  // Search "BUFR" string
  unsigned long n = NorBufrIO::findBytes(is, "BUFR", 4);
  if (n == ULONG_MAX) {
    bufr.lb.addLogEntry(LogEntry("No more BUFR messages", LogLevel::INFO,
                                 __func__, bufr.bufr_id));
    return is;
  }

  bufr.lb.addLogEntry(
      LogEntry("BUFR Section found at: " + std::to_string(is.tellg()),
               LogLevel::DEBUG, __func__, bufr.bufr_id));
  is.seekg(static_cast<std::streampos>(n), std::ios_base::beg);

  // Section0 length
  const int slen = 8;
  uint8_t sec0[slen];
  is.read(reinterpret_cast<char *>(sec0), slen);

  bufr.len = NorBufrIO::getBytes(sec0 + 4, 3);
  bufr.edition = sec0[7];

  bufr.lb.addLogEntry(LogEntry("BUFR Size: " + std::to_string(bufr.len) +
                                   " Edition: " + std::to_string(bufr.edition),
                               LogLevel::DEBUG, __func__, bufr.bufr_id));

  bufr.buffer = new uint8_t[bufr.len];
  memcpy(bufr.buffer, sec0, slen);

  is.read(reinterpret_cast<char *>(bufr.buffer + slen), bufr.len - slen);
  std::streamsize rchar = is.gcount();

  if (rchar != bufr.len - slen) {
    bufr.lb.addLogEntry(
        LogEntry("Reading Error", LogLevel::ERROR_, __func__, bufr.bufr_id));
    bufr.len = rchar + slen - 1;
  }

  int offset = bufr.checkBuffer();

  // "rewind" filepos
  if (offset && is.good()) {
    bufr.lb.addLogEntry(
        LogEntry("Seek stream to next:" + std::to_string(offset),
                 LogLevel::WARN, __func__, bufr.bufr_id));
    is.seekg(offset, std::ios_base::cur);
  }

  bufr.setSections(slen);

  return is;
}

bool NorBufr::setSections(int slen) {

  // Section1 load
  Section1::fromBuffer(buffer + slen, len - slen, edition);
  slen += Section1::length();

  // Section2 load, if exists
  if (optSection()) {
    Section2::fromBuffer(buffer + slen, len - slen);
    slen += Section2::length();
  }

  // Section3 load
  if (Section3::fromBuffer(buffer + slen, len - slen)) {
    if (Section3::length()) {
      slen += Section3::length();
      subsets.resize(subsetNum());
      desc.resize(subsetNum());

      // Section 4 load
      if (Section4::fromBuffer(buffer + slen, len - slen)) {
        lb.addLogEntry(
            LogEntry("BUFR loaded", LogLevel::DEBUG, __func__, bufr_id));
      } else {
        lb.addLogEntry(
            LogEntry("Corrupt Section4", LogLevel::ERROR_, __func__, bufr_id));
        return false;
      }
    } else {
      lb.addLogEntry(LogEntry("Section3 size error, skip", LogLevel::ERROR_,
                              __func__, bufr_id));
      return false;
    }
  } else {
    lb.addLogEntry(LogEntry("Section3 load error, skip Section4",
                            LogLevel::ERROR_, __func__, bufr_id));
    return false;
  }

  return true;
}

long NorBufr::checkBuffer() {
  const char *start = "BUFR";
  int si = 0;
  int ei = 0;

  long offset = 0;

  if (len >= 8) {
    for (int i = 4; i < len; ++i) {
      if (buffer[i] == start[si]) {
        si++;
        if (si == 4) {
          lb.addLogEntry(
              LogEntry("Found new BUFR sequence at:" + std::to_string(i - 4),
                       LogLevel::ERROR_, __func__, bufr_id));
          offset = i - len - 4;
          len = i - 4;
          break;
        }
      } else {
        if (buffer[i] == start[0])
          si = 1;
        else
          si = 0;
      }
      if (buffer[i] == '7') {
        ei++;
        if (ei == 4 && i != len - 1) {
          lb.addLogEntry(LogEntry("Found end sequence at:" + std::to_string(i),
                                  LogLevel::ERROR_, __func__, bufr_id));
          offset = i - len;
        }
      } else
        ei = 0;
    }
  }

  return offset;
}

bool NorBufr::fromText(std::istream &is) {

  encode_descriptors.clear();

  int f, x, y;
  while (is >> f >> x >> y) {
    if (f || x || y) {
      encodeDescriptor(DescriptorId(f, x, y), is);
    } else {
      encodeSubsets(is);
      break;
    }
  }

  len = 8 + Section1::len + Section2::len + Section3::len + Section4::len + 4;

  return true;
}

bool NorBufr::fromCovJson(std::string) { return true; }

uint64_t NorBufr::encodeSubsets(std::istream &is) {
  std::string v;
  uint64_t add_subset_size = 0;
  const size_t line_max = 1000;
  char line[line_max];

  for (int i = 1; i < Section3::subsets; ++i) {
    for (typename std::list<std::pair<DescriptorId, std::vector<int>>>::iterator
             it = encode_descriptors.begin();
         it != encode_descriptors.end(); ++it) {

      is >> v;
      if (v == "missing" || v == "MISSING" || v == "Missing") {
        Section4::setMissingValue(it->second[0]);
        add_subset_size += it->second[0];
        continue;
      }
      if (tabB->at(it->first).unit() == "CCITTIA5") {
        is.getline(line, line_max);
        std::string line_str(line);
        v += line_str;

        for (int ii = 0; ii < it->second[0] / 8; ++ii) {
          if (ii < static_cast<int>(v.size()))
            Section4::setValue(v[ii], 8);
          else
            Section4::setValue(' ', 8); // space
          add_subset_size++;
        }
      } else {
        long double dvalue;
        std::stringstream ss;
        ss << v;
        ss >> dvalue;
        unsigned long value = dvalue;

        if (it->second.size() > 1) {
          int sc = it->second[1];
          int ref = it->second[2];
          if (sc != 0) {
            dvalue = dvalue * (pow(10.0, sc));
          }
          if (ref != 0) {
            dvalue -= ref;
          }
          value = dvalue;
        }
        Section4::setValue(value, it->second[0]);
        add_subset_size += it->second[0];
      }
    }
  }

  return add_subset_size;
}

bool NorBufr::encodeDescriptor(DescriptorId D, std::istream &is, int level,
                               DescriptorId *parent, int index) {

  if (level == 0)
    Section3::addDescriptor(D);
  const size_t line_max = 1000;
  char line[line_max];

  switch (D.f()) {
  case 0: {

    int sc = tabB->at(D).scale() + enc_mod_scale;
    int ref = 0;
    if (enc_mod_refvalue_mul != 0)
      ref = enc_mod_refvalue_mul;
    if (tabB->at(D).reference() != 0) {
      ref += tabB->at(D).reference();
    }

    if (D.x() != 31) {
      std::string v;
      is >> v;
      std::transform(v.begin(), v.end(), v.begin(), ::toupper);
      if (v == "MISSING") {
        int cdatawidth = tabB->at(D).datawidth() + enc_mod_datawidth;
        if (tabB->at(D).unit().find("CODE TABLE") != std::string::npos)
          cdatawidth -= enc_mod_datawidth;
        Section4::setMissingValue(cdatawidth);
        std::vector<int> datamod;
        datamod.push_back(cdatawidth);
        if (sc != 0 || ref != 0) {
          datamod.push_back(sc);
          datamod.push_back(ref);
        }

        encode_descriptors.push_back(std::make_pair(D, datamod));
        is.getline(line, line_max);

        break;
      }
      if (tabB->at(D).unit().substr(0, 8) == "CCITTIA5") {
        unsigned int dw = enc_mod_str_datawidth
                              ? enc_mod_str_datawidth
                              : tabB->at(D).datawidth() + enc_mod_datawidth;
        if (v.size() < dw / 8) {
          is.getline(line, dw / 8);
          std::string line_str(line);
          v += line_str;
        }
        for (unsigned int i = 0; i < dw / 8; ++i) {
          Section4::setValue(i < v.size() ? v[i] : ' ', 8);
        }
        std::vector<int> datamod;
        datamod.push_back(dw);
        encode_descriptors.push_back(std::make_pair(D, datamod));

      } else {
        std::string::size_type sz;
        long double dvalue = std::stold(v, &sz);

        if (sc != 0)
          dvalue = dvalue * (pow(10.0, sc));
        if (enc_mod_refvalue_mul != 0)
          dvalue -= enc_mod_refvalue_mul;
        else {
          if (tabB->at(D).reference() != 0)
            dvalue -= tabB->at(D).reference();
        }
        uint64_t value = dvalue;
        Section4::setValue(value, tabB->at(D).datawidth() + enc_mod_datawidth);
        std::vector<int> datamod;
        datamod.push_back(tabB->at(D).datawidth() + enc_mod_datawidth);
        if (sc != 0 || ref != 0) {
          datamod.push_back(sc);
          datamod.push_back(ref);
        }

        encode_descriptors.push_back(std::make_pair(D, datamod));

        // Set BUFR Date and Time (Section1)
        if (auto_date) {
          if ((D.x() == 4) && (D.y() < 7)) {
            switch (D.y()) {
            case 1:
              Section1::setYear(value);
              break;
            case 2:
              Section1::setMonth(value);
              break;
            case 3:
              Section1::setDay(value);
              break;
            case 4:
              Section1::setHour(value);
              break;
            case 5:
              Section1::setMinute(value);
              if (edition < 4)
                auto_date = false;
              break;
            case 6:
              Section1::setSecond(value);
              auto_date = false;
              break;
            }
          }
        }
      }
    } else {
      long value;
      is >> value;

      Section4::setValue(value, tabB->at(D).datawidth() + enc_mod_datawidth);
      std::vector<int> datamod;
      datamod.push_back(tabB->at(D).datawidth() + enc_mod_datawidth);
      encode_descriptors.push_back(std::make_pair(D, datamod));
    }
    break;
  }
  case 1: {
    int f, x, y;
    int descnum = D.x();
    long repeatnum;
    std::list<DescriptorId> ddtree;
    typename std::list<DescriptorId>::iterator it; // = ddtree.begin();
    if (D.y() != 0)
      repeatnum = D.y();
    else {
      DescriptorId d;
      if (level == 0) {
        is >> f >> x >> y;
        DescriptorId dd(f, x, y);
        d = dd;
      } else {
        if (parent->f() == 0) {
          d = *parent;
        } else {
          ddtree = tabD->expandDescriptor(*parent);
          it = ddtree.begin();
          for (int i = 0; i <= index + 1; ++i) {
            d = *it;
            ++it;
          }
        }
      }
      encodeDescriptor(d, is, level);
      unsigned long urep =
          Section4::getValue(Section4::bitSize() - tabB->at(d).datawidth(),
                             tabB->at(d).datawidth() + enc_mod_datawidth);
      repeatnum = urep;
    }
    std::vector<DescriptorId> dv(descnum);
    std::vector<std::string> dvalue(descnum);
    std::vector<std::streampos> position(descnum);
    std::streampos endpos;
    for (int i = 0; i < descnum; ++i) {
      if (level == 0) {
        f = x = y = 0;

        char line[1024];
        is.getline(line, 1024);
        std::istringstream iss(line);
        if (!(iss >> f >> x >> y)) {
          --i;
          if (!is.good())
            break;
          continue;
        }
        position[i] = is.tellg();

        DescriptorId d(f, x, y);
        dv[i] = d;
        if (d.f() == 0 && repeatnum > 0) {
          is >> dvalue[i];
        }
      } else {
        if (parent->f() == 1 || parent->f() == 0) {
          dv[i] = *(parent + i + 1);
        } else {
          if (D.f() == 1 && ddtree.size() == 0) {
            ddtree = tabD->expandDescriptor(*parent);
            it = ddtree.begin();
            int ii_ndx = 0;
            for (size_t dt_elem = 0; dt_elem < ddtree.size(); ++dt_elem) {
              if (ii_ndx < index - 2) {
                ++it;
              }
              ++ii_ndx;
            }
            for (size_t i = 0; i < dv.size(); ++i) {
              ++it;
              dv[i] = *it;
            }
          }

          dv[i] = *it;
          ++it;
        }
        position[i] = is.tellg();
        if (dv[i].f() == 0 && repeatnum > 0) {
          is >> dvalue[i];
        }
      }
      if (0 == repeatnum) {
        Section3::addDescriptor(dv[i]);
      }
    }
    endpos = is.tellg();

    if (repeatnum > 0) {
      for (int i = 0; i < descnum; ++i) {
        is.seekg(position[i], std::ios_base::beg);
        encodeDescriptor(dv[i], is, level);
        if (dv[i].f() == 1) {
          std::streampos retpos = is.tellg();
          for (int ii = 0; ii < descnum; ++ii) {
            if (position[ii] > retpos) {
              i = ii - 1;
              break;
            }
          }
        }
      }

      for (int j = 1; j < repeatnum; ++j) {
        for (int i = 0; i < descnum; ++i) {
          if (dv[i].f() == 1) {
            if (dv[i].y())
              encodeDescriptor(dv[i], is, level + 1, &(dv[i]));
            else
              encodeDescriptor(dv[i], is, level + 1, &(dv[i + 1]));
          } else {
            encodeDescriptor(dv[i], is, level + 1);
          }
          if (dv[i].f() == 1) {
            i += dv[i].x() + 1;
          }
        }
      }
    }

    break;

    break;
  }
  case 2: {
    std::cerr << "Descriptor mod: " << D << " Not yet implemented!!!\n";
    break;
  }
  case 3: {
    std::list<DescriptorId> dtree = tabD->expandDescriptor(D);
    int subindex = 0;
    for (typename std::list<DescriptorId>::iterator it = dtree.begin();
         it != dtree.end(); ++it) {
      encodeDescriptor(*it, is, level + 1, &D, subindex++);
      if (it->f() == 1) {
        int skip = it->x();
        if (it->y() == 0)
          ++skip;
        for (int i = 0; i < skip; ++i) {
          ++it;
          if (it == dtree.end())
            break;
        }
      }
    }

    break;
  }
  }
  return true;
}

void NorBufr::print(DescriptorId df, std::string filter,
                    DescriptorId dv) const {

  for (size_t i = 0; i < desc.size(); ++i) {
    // std::cerr << "Find subset: " << i << "\n";
    auto it = std::find(desc[i].begin(), desc[i].end(), df);
    if (it != desc[i].end()) {
      // std::cerr << " Desc match :" << getValue(*it,std::string(),false) << ":
      // ";
      if (getValue(*it, std::string(), false) == filter) {
        // std::cerr << " Filter match " ;
        auto dvit = std::find(it, desc[i].end(), dv);
        if (dvit != desc[i].end()) {
          std::string dt(asctime(&bufr_time));
          dt.erase(std::remove(dt.begin(), dt.end(), '\n'), dt.end());
          std::cout << dt << " " << df << "=" << filter << " => " << dv << "="
                    << getValue(*dvit, std::string()) << "\n";
        }
      }
    }
  }
}

void NorBufr::printValue(DescriptorId df) const {
  for (size_t i = 0; i < desc.size(); ++i) {
    // std::cerr << "Find subset: " << i << "\n";
    auto it = std::find(desc[i].begin(), desc[i].end(), df);
    if (it != desc[i].end()) {
      std::string v = getValue(*it, std::string(), false);
      if (v.size())
        std::cout << v << " ";
    }
  }
}

void NorBufr::setBufrId(std::string s) { bufr_id = s; }

void NorBufr::logToCsvList(std::list<std::string> &list, char delimiter,
                           LogLevel l) const {
  lb.toCsvList(list, delimiter, l);
}

void NorBufr::logToJsonList(std::list<std::string> &list, LogLevel l) const {
  lb.toJsonList(list, l);
}

std::ostream &NorBufr::printDetail(std::ostream &os) {
  os << std::dec;
  os << "********************************** B U F R "
        "********************************************\n";
  os << "=============== Section 0  ===============\n";
  os << "length: " << len << " Edition: " << static_cast<int>(edition) << "\n";

  os << static_cast<Section1 &>(*this);
  os << static_cast<Section2 &>(*this);
  os << static_cast<Section3 &>(*this);
  os << static_cast<Section4 &>(*this);
  os << "Subsetbits: ";
  for (auto v : subsets) {
    os << v << " ";
  }
  os << "\n";

  os << "********************************** EXPANDED DESCRIPTORS  "
        "********************************************\n";

  int subsetnum = 0;
  for (auto s : desc) {
    os << "\n ===================================== S U B S E T "
       << subsetnum + 1 << " =====================================\n\n";
    for (auto v : s) {
      v.printDetail(os);
      DescriptorMeta *meta = v.getMeta();
      if (meta) {
        os << " [sb: " << v.startBit() << "] ";
        // New Reference value in the name string
        if (meta->unit() != "Reference")
          os << getValue(v, std::string());

        if (meta->unit().find("CODE TABLE") != std::string::npos ||
            meta->unit().find("FLAG TABLE") != std::string::npos) {
          os << " [code:";
          uint64_t cval =
              NorBufrIO::getBitValue(v.startBit(), meta->datawidth(), true,
                                     (isCompressed() ? ucbits : bits));
          if ((std::numeric_limits<uint64_t>::max)() != cval) {
            os << cval;
          }
          os << "]";
        }
        os << "\t\tbits:"
           << NorBufrIO::getBitStrValue(v.startBit(), meta->datawidth(),
                                        (isCompressed() ? ucbits : bits));
        if (meta->assocwidth() > 0) {
          os << "\tassocbits:"
             << NorBufrIO::getBitStrValue(v.startBit() - meta->assocwidth(),
                                          meta->assocwidth(),
                                          (isCompressed() ? ucbits : bits));
        }
        os << " \t\tMeta: ";
        os << " " << meta->name() << " unit: " << meta->unit();
      }
      os << "\n";
    }
    subsetnum++;
  }

  os << "\n";
  os << "********************************** E N D B U F R "
        "********************************************\n";

  return os;
}

std::ostream &operator<<(std::ostream &os, NorBufr &bufr) {
  os << std::dec;
  os << "\n********************************************************************"
        "*******************\n";
  os << "********************************** B U F R "
        "********************************************\n";
  os << "**********************************************************************"
        "*****************\n\n";
  os << "=============== Section 0  ===============\n";
  os << "length: " << bufr.len << " Edition: " << static_cast<int>(bufr.edition)
     << "\n";

  os << static_cast<Section1 &>(bufr);
  os << static_cast<Section2 &>(bufr);
  os << static_cast<Section3 &>(bufr);
  os << static_cast<Section4 &>(bufr);

  os << "\n********************************************************************"
        "*******************\n";
  os << "************************ EXPANDED DESCRIPTORS AND DATA  "
        "*******************************\n";
  os << "**********************************************************************"
        "*****************\n";

  int subsetnum = 0;
  for (auto s : bufr.desc) {
    os << "\n=============== S U B S E T " << subsetnum + 1
       << " ===============\n\n";
    for (auto v : s) {
      os << v;
      DescriptorMeta *meta = v.getMeta();
      if (meta) {
        // New Reference value in the name string
        if (meta->unit() != "Reference")
          os << "\t" << bufr.getValue(v, std::string());

        if (meta->unit().find("CODE TABLE") != std::string::npos ||
            meta->unit().find("FLAG TABLE") != std::string::npos) {
          os << " [code:";
          uint64_t cval = NorBufrIO::getBitValue(
              v.startBit(), meta->datawidth(), true,
              (bufr.isCompressed() ? bufr.ucbits : bufr.bits));
          if ((std::numeric_limits<uint64_t>::max)() != cval) {
            os << cval;
          }
          os << "]";
        }
        os << "\t\t" << meta->name();
      }
      os << "\n";
    }
    subsetnum++;
  }

  os << "\n";
  os << "**********************************************************************"
        "*****************\n";
  os << "******************************* E N D B U F R "
        "*****************************************\n";
  os << "**********************************************************************"
        "*****************\n";

  return os;
}
