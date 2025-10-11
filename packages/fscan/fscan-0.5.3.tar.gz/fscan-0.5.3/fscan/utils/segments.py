# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) Evan Goetz (2023-2025)
#
# This file is part of fscan

import numpy as np
from pathlib import Path
from gwpy.segments import Segment, SegmentList, DataQualityDict
from gwdatafind import find_urls
from gwdatafind.utils import file_segment


def find_segments(epseg_info, intersect_data=False):
    """
    This queries the segment database for the specified segment type.

    By default, this will query <ifo>:DMT-ANALYSIS_READY.
    If a segment file (or ALL) is given, then just copy over the segment
    file specified to the SFTpath / epoch directory
    """
    SFTGPSstart = epseg_info['GPSstart']  # initial value, may be amended later
    GPSend = epseg_info['GPSstart'] + epseg_info['duration']
    step = epseg_info['Tsft'] * (1 - epseg_info['overlap_fraction'])
    span_start = span_end = None

    # If there's already a segment file, we don't need to make one.
    # We'll just read from it (at the end of this function) to make
    # sure the correct start and end times are recorded.
    if Path(epseg_info['segfile']).exists():
        # Read from the segment file to return the updated start and
        # end GPS (this will be necessary to correctly name plots and
        # configure summary pages).
        segdat = np.genfromtxt(epseg_info['segfile'], dtype='int')
        if len(segdat) == 0:
            return None, None
        else:
            segdat = np.atleast_2d(segdat)
            return segdat[0][0], segdat[-1][-1]
    else:
        if epseg_info['segtype'] == ['ALL']:
            print("Using all available data with no segment type restriction")
            segs = SegmentList([Segment(epseg_info['GPSstart'], GPSend)])

        # If no segment file given, and segment type isn't 'ALL',
        # then query the segment database
        else:
            print("Querying segments")
            dqdict = DataQualityDict.query_dqsegdb(
                    epseg_info['segtype'],
                    epseg_info['GPSstart'],
                    GPSend)
            segs = dqdict.intersection().active
            if len(segs) == 0:
                Path(epseg_info['segfile']).touch(exist_ok=True)
                return None, None
            # If the earliest segment goes all the way to the starting
            # cutoff point, look back 1 week. We are looking for the point
            # where the flag actually became active
            lookback_window = 7*24*60*60  # TODO: handle smarter
            if segs[0][0] <= epseg_info['GPSstart']:
                prev_epoch_segs = DataQualityDict.query_dqsegdb(
                    epseg_info['segtype'],
                    epseg_info['GPSstart'] - lookback_window,
                    epseg_info['GPSstart']).intersection().active

                prev_epoch_segstart = int(prev_epoch_segs[-1][0])

                # Align the segments to an integer multiple of 'step'
                # counting from the point where the flag became active
                SFTGPSstart = (
                    epseg_info['GPSstart'] +
                    (step - (epseg_info['GPSstart'] - prev_epoch_segstart) %
                     step))
                SFTGPSstart = int(SFTGPSstart)
                print(f"Aligning segments to a new start time: {SFTGPSstart}")

        # If requested, here we find the data first and check if it is
        # available and intersect with the requested segments
        if intersect_data:
            for frametype in epseg_info['frametypes']:
                # query for the data of this frametype, spit out a warning if
                # some data is not available
                urls = find_urls(frametype[0], frametype, SFTGPSstart, GPSend,
                                 on_missing='warn')

                # create a segment list from each of the frame files
                data_segs = SegmentList()
                for url in urls:
                    data_segs.append(Segment(file_segment(url)))

                # merge (coalesce) the data file segments
                data_segs.coalesce()

                # remove any segments with length less than Tsft
                data_segs_copy = data_segs.copy()
                for seg in data_segs:
                    if abs(seg) < epseg_info['Tsft']:
                        data_segs_copy.remove(seg)
                data_segs = data_segs_copy.copy()

                # adjust data segments beyond the first to start an integer
                # number of steps after the SFT GPS start time. segments are
                # required to be of length Tsft or longer to be added to the
                # modified data segments list
                modified_data_segs = SegmentList()
                for seg in data_segs:
                    # numsteps should always be 0 or larger
                    numsteps = max(
                        0, int(np.ceil((seg[0] - SFTGPSstart)/step)))
                    newseg = Segment(SFTGPSstart + numsteps*step, seg[1])
                    if abs(newseg) >= epseg_info['Tsft']:
                        modified_data_segs.append(newseg)

                # intersect with original data quality segs
                segs &= modified_data_segs

        with open(epseg_info['segfile'], 'w') as f:
            for seg in segs:

                # This is done for 2 reasons:
                # (a) because dqsegdb2 has historically returned
                # GPS times outside the range requested, and (b)
                # because the SFTGPSstart is adjusted (possibly moved
                # later) relative to the GPSstart that was initially
                # used to query the segments.
                if int(seg[0]) < SFTGPSstart:
                    seg = Segment(SFTGPSstart, seg[1])

                # This is just compensating for the dqsegdb2 issue
                # described above
                if int(seg[1]) > GPSend:
                    seg = Segment(seg[0], GPSend)

                # Don't use this segment if it is less than Tsft long
                if abs(seg) < epseg_info['Tsft']:
                    continue

                # This is because any extra time around the SFTs will
                # cause lalpulsar_MakeSFTDAG to "center" the SFTs in a
                # way that causes inconsistencies between avg durations
                nsteps = int(np.floor((abs(seg) - epseg_info['Tsft']) / step))
                seg = Segment(seg[0],
                              seg[0] + (nsteps * step) + epseg_info['Tsft'])

                # write this segment to the segment file
                f.write(f"{int(seg[0])} {int(seg[1])}\n")

                # set span start and end
                if not span_start:
                    span_start = int(seg[0])
                span_end = int(seg[-1])

    # Return None, None if no data or segments are longer than Tsft
    # otherwise return start of first segment and end of last segment
    return span_start, span_end
