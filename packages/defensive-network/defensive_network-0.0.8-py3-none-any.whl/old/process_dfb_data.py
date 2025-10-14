"""
Preprocess the monolithic DFB data into a more manageable format.

Preprocessed files:
- lineups.csv
- meta.csv
- events/{match_string}.csv
- tracking/{match_string}.parquet
"""

import gc
import math
import os

import pandas as pd
import slugify
import streamlit as st

import sys

import defensive_network.utility.dataframes

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import defensive_network.utility.general


@st.cache_resource
def _read_df(fpath, **kwargs):
    return pd.read_csv(fpath, **kwargs)


def get_dfb_csv_files_in_folder(folder, exclude_files=None):
    tracking_cols = "frame,match_id,player_id,team_id,event_vendor,tracking_vendor,datetime_tracking,section,x_tracking,y_tracking,z_tracking,d_tracking,a_tracking,s_tracking,ball_status,ball_poss_team_id"
    event_cols = "frame,match_id,event_id,event_vendor,tracking_vendor,datetime_event,datetime_tracking,event_type,event_subtype,event_outcome,player_id_1,team_id_1,player_id_2,team_id_2,x_event,y_event,x_tracking_player_1,y_tracking_player_1,x_tracking_player_2,y_tracking_player_2,section,xg,xpass,player_pressure_1,player_pressure_2,assist_action,assist_type,rotation_ball,foot,direction,origin_setup,foul_type,card_color,reason,frame_rec,packing_traditional,packing_horizontal,packing_vertical,packing_attention"
    lineup_cols = "match_id,event_vendor,tracking_vendor,team_id,team_name,team_role,player_id,jersey_number,first_name,last_name,short_name,position_group,position,starting,captain"
    meta_cols = "competition_name,competition_id,host,match_day,season_name,season_id,kickoff_time,match_id,event_vendor,tracking_vendor,match_title,home_team_name,home_team_id,guest_team_name,guest_team_id,result,country,stadium_id,stadium_name,precipitation,pitch_x,pitch_y,total_time_first_half,total_time_second_half,playing_time_first_half,playing_time_second_half,ds_parser_version,xg_tag,xg_sha1,xpass_tag,xpass_sha1,fps"

    csv_files = [f for f in os.listdir(folder) if f.endswith(".csv")]
    header_to_filetype = {
        tracking_cols: "tracking",
        event_cols: "event",
        meta_cols: "meta",
        lineup_cols: "lineup",
    }
    filetype_to_files = {}
    for csv_file in csv_files:
        st.write(csv_file)
        if csv_file.startswith("._"):
            continue
        full_csv_file = os.path.join(folder, csv_file)
        if exclude_files is not None and full_csv_file in exclude_files:
            continue
        with open(full_csv_file) as f:
            first_line = f.readline().strip()
        file_type = header_to_filetype[first_line]  # If not successful, the file is wrong -> check manually
        filetype_to_files[file_type] = filetype_to_files.get(file_type, []) + [full_csv_file]

    return filetype_to_files


def process_meta(files, target_fpath, overwrite_if_exists=True):
    if not overwrite_if_exists and os.path.exists(target_fpath):
        return
    dfs = []
    for file in files:
        df_meta = _read_df(file)
        df_meta["match_string"] = df_meta.apply(lambda row: f"{row['competition_name']} {row['season_name']}: {row['match_day']}.ST {row['match_title'].replace('-', ' - ')}", axis=1)
        df_meta["slugified_match_string"] = df_meta["match_string"].apply(slugify.slugify)
        dfs.append(df_meta)
    df_meta = pd.concat(dfs, axis=0)
    st.write(f"Wrote df_meta to {target_fpath}")
    st.write(df_meta)
    df_meta.to_csv(target_fpath)


def process_lineups(files, target_fpath, overwrite_if_exists=True):
    if not overwrite_if_exists and os.path.exists(target_fpath):
        return
    dfs = []
    for file in files:
        df_lineup = _read_df(file)
        dfs.append(df_lineup)
    df_lineup = pd.concat(dfs, axis=0)
    df_lineup = df_lineup.replace(-9999, None)  # weird DFB convention to use -9999 for missing values
    df_lineup.to_csv(target_fpath)
    st.write(f"Wrote df_lineup to {target_fpath}")
    st.write(df_lineup)
    return df_lineup


def process_events(raw_event_paths, preprocessed_events_folder, meta_fpath, folder_tracking, overwrite_if_exists=True):
    if not os.path.exists(preprocessed_events_folder):
        os.makedirs(preprocessed_events_folder)

    def get_target_x_y(row, df_tracking_indexed):
        receiver = row["player_id_2"]
        try:
            receiver_frame = df_tracking_indexed.loc[(row["frame_rec"], row["section"], receiver)]
            return receiver_frame["x_tracking"], receiver_frame["y_tracking"]
        except KeyError:
            return None, None

    dfs = [_read_df(events_fpath) for events_fpath in raw_event_paths]
    df_events = pd.concat(dfs, axis=0)
    df_events = df_events.replace(-9999, None)
    df_meta = _read_df(meta_fpath)
    df_events = df_events.merge(df_meta[["match_id", "slugified_match_string", "match_string"]], on="match_id")
    for match_id, df_events_match in df_events.groupby("match_id"):
        slugified_match_string = df_events_match["slugified_match_string"].iloc[0]
        match_string = df_events_match["match_string"].iloc[0]
        target_fpath = os.path.join(preprocessed_events_folder, f"{slugified_match_string}.csv")
        if not overwrite_if_exists and os.path.exists(target_fpath):
            continue

        try:
            df_tracking = pd.read_parquet(os.path.join(folder_tracking, f"{slugified_match_string}.parquet"))
        except FileNotFoundError:
            df_tracking = None
            st.warning(f"Tracking data not found for match {match_string}")

        if df_tracking is not None:
            df_tracking_indexed = df_tracking.set_index(["frame", "section", "player_id"])
            with st.spinner("Calculating target x, y from tracking data..."):
                keys = df_events_match.apply(lambda row: get_target_x_y(row, df_tracking_indexed), axis=1)

            df_events_match[["x_target", "y_target"]] = pd.DataFrame(keys.tolist(), index=df_events_match.index)
            df_events_match["x_target"] = df_events_match["x_target"].fillna(df_events_match["x_tracking_player_2"])
            df_events_match["y_target"] = df_events_match["y_target"].fillna(df_events_match["y_tracking_player_2"])

            st.write("df_events_match")
            st.write(df_events_match)
        df_events_match.to_csv(target_fpath, index=False)
    st.write(f"Saved events to {preprocessed_events_folder}")


def process_tracking(files, target_folder, fpath_meta, chunksize=5e5):
    # TODO overwrite_if_exists not implemented yet - would probably make it much faster, but how to do it?
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    for file in defensive_network.utility.general.progress_bar(files, desc=f"Processing tracking files ({len(files)} found)"):
        st.write(f"Processing tracking file {file} [chunksize={chunksize}]")

        @st.cache_resource
        def _get_n_lines(file):
            return defensive_network.utility.general.get_number_of_lines_in_file(file)

        n_lines = _get_n_lines(file)
        st.write(f"{n_lines=}")

        def _partition_by_match(_df_chunk, _target_folder, fpath_meta):
            df_meta = _read_df(fpath_meta)
            for match_id, df_match_chunk in _df_chunk.groupby("match_id"):
                slugified_match_string = df_meta[df_meta["match_id"] == match_id]["slugified_match_string"].iloc[0]
                fpath_match = os.path.join(_target_folder, f"{slugified_match_string}.parquet")
                st.write(f"Processing match {match_id} ({fpath_match})")

                ### Assertions that take too much time
                # df_nan = df_match_chunk[df_match_chunk[["frame", "player_id"]].isna().all(axis=1)]
                # if len(df_nan) > 0:
                #     st.write("df_nan")
                #     st.write(df_nan)
                #     raise ValueError("NaN values in frame or player_id")

                # df_partial_duplicates = df_chunk[df_chunk.duplicated(subset=["match_id", "section", "frame", "player_id"], keep=False)]
                # assert len(df_partial_duplicates) == 0

                defensive_network.utility.dataframes.append_to_parquet_file(df_match_chunk, fpath_match, key_cols=["match_id", "section", "frame", "player_id"], overwrite_key_cols=True)

        with pd.read_csv(file, chunksize=chunksize, delimiter=",") as reader:
            total = math.ceil(n_lines / chunksize)
            for df_chunk in defensive_network.utility.general.progress_bar(reader, total=total, desc="Reading df_tracking in chunks"):
                _partition_by_match(df_chunk, target_folder, fpath_meta)
                del df_chunk
                gc.collect()


def check_tracking_files(folder):
    for file in os.listdir(folder):
        if not file.endswith(".parquet"):
            continue
        fpath = os.path.join(folder, file)
        df = pd.read_parquet(fpath)
        st.write(fpath)
        for section, df_section in df.groupby("section"):
            if not len(df_section["frame"].unique()) == df_section["frame"].max() - df_section["frame"].min() + 1:
                st.error(f"Missing frames in {section} of {fpath}")
            else:
                st.write(section, df_section["frame"].min(), df_section["frame"].max(), "OK")


def main():
    overwrite_if_exists = True
    # overwrite_if_exists = st.toggle("Overwrite if exists", value=True)
    _process_meta = st.toggle("Process meta", value=False)
    _process_lineups = st.toggle("Process lineups", value=False)
    _process_events = st.toggle("Process events", value=False)
    _process_tracking = st.toggle("Process tracking", value=False)
    _check_tracking_files = st.toggle("Check tracking files", value=False)
    folder = st.text_input("Folder", "C:/Users/Jonas/Downloads/dfl_test_data/2324/")
    if not os.path.exists(folder):
        st.error(f"Folder {folder} does not exist")
        return
    fpath_target_meta = st.text_input("Processed meta.csv file", os.path.join(folder, "meta.csv"))
    fpath_target_lineup = st.text_input("Processed lineup.csv file", os.path.join(folder, "lineup.csv"))
    folder_events = st.text_input("Folder for preprocessed events", os.path.join(folder, "events"))
    folder_tracking = st.text_input("Folder for preprocessed tracking", os.path.join(folder, "tracking"))

    filetype_to_files = get_dfb_csv_files_in_folder(folder, [fpath_target_meta, fpath_target_lineup])
    st.write("Found files:", filetype_to_files)

    if _process_meta:
        process_meta(filetype_to_files["meta"], fpath_target_meta, overwrite_if_exists)
    if _process_lineups:
        process_lineups(filetype_to_files["lineup"], fpath_target_lineup, overwrite_if_exists)
    if _process_tracking:
        chunksize = st.number_input("Rows per chunk of tracking data (more = faster but consumes more RAM)", min_value=1, value=500000)
        process_tracking(filetype_to_files["tracking"], folder_tracking, fpath_target_meta, chunksize)
    if _process_events:
        process_events(filetype_to_files["event"], folder_events, fpath_target_meta, folder_tracking, overwrite_if_exists)
    if _check_tracking_files:
        check_tracking_files(folder_tracking)


def concat_metas_and_lineups():
    for kind, path in [
        ("meta", "C:/Users/Jonas/Downloads/dfl_test_data/2324/meta"),
        ("lineup", "C:/Users/Jonas/Downloads/dfl_test_data/2324/lineup"),
    ]:
        files = os.listdir(path)
        dfs = []
        for file in files:
            fpath = os.path.join(path, file)
            df = pd.read_csv(fpath)
            dfs.append(df)
        df_meta = pd.concat(dfs, axis=0)
        df_meta.to_csv(f"C:/Users/Jonas/Downloads/dfl_test_data/2324/{kind}.csv", index=False)


if __name__ == '__main__':
    concat_metas_and_lineups()
    main()
