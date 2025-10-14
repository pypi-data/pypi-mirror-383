import numpy as np
import pandas as pd
import polars as pl

import artistools as at

CLIGHT = 2.99792458e10


def change_cell_positions_to_new_time(dfgriddata: pd.DataFrame, t_model_1d: float) -> tuple[pd.DataFrame, float]:
    dfgriddata["pos_x_min"] = dfgriddata["vel_x_min"] * t_model_1d
    dfgriddata["pos_y_min"] = dfgriddata["vel_y_min"] * t_model_1d
    dfgriddata["pos_z_min"] = dfgriddata["vel_z_min"] * t_model_1d

    ngridcells = len(dfgriddata["pos_x_min"])
    ncoordgridx = round(ngridcells ** (1.0 / 3.0))
    wid_init = 2 * max(dfgriddata["pos_x_min"]) / ncoordgridx
    return dfgriddata, wid_init


def map_1d_to_3d(
    dfgriddata: pd.DataFrame,
    vmax: float,
    n_3d_gridcells: int,
    data_1d: pd.DataFrame,
    t_model_1d: float,
    wid_init: float,
) -> None:
    modelgridindex = np.zeros(n_3d_gridcells)
    modelgrid_rho_3d = np.zeros(n_3d_gridcells)
    modelgrid_mid_vel = np.zeros(n_3d_gridcells)
    EMPTYGRIDCELL = -99
    vmax_map = 0.25

    for n_3d, row in dfgriddata.iterrows():
        radial_vel_mid = at.vec_len([
            row["posx_mid"] / t_model_1d / CLIGHT,
            row["posy_mid"] / t_model_1d / CLIGHT,
            row["posz_mid"] / t_model_1d / CLIGHT,
        ])
        assert isinstance(n_3d, int)
        if n_3d % 1000 == 0:
            print(f"mapping cell {n_3d} of {n_3d_gridcells}")

        if radial_vel_mid < vmax_map:
            for m_1d, radial_vel_1d in enumerate(data_1d["velocity"]):
                if radial_vel_1d < radial_vel_mid:
                    modelgridindex[n_3d] = m_1d  # index of outermost 1d cell at 3d cell midpoint
                    modelgrid_rho_3d[n_3d] = data_1d["rho_torus"][m_1d]  # associated rho
                    modelgrid_mid_vel[n_3d] = radial_vel_mid  # associated rho
        else:
            modelgridindex[n_3d] = EMPTYGRIDCELL

    dfgriddata["rho"] = modelgrid_rho_3d
    dfgriddata["vel_mid"] = modelgrid_mid_vel
    print(dfgriddata)
    print(sum(modelgrid_rho_3d * (wid_init**3)) / CLIGHT)

    at.inputmodel.save_modeldata(
        dfmodel=pl.from_pandas(dfgriddata), t_model_init_days=t_model_1d / (24 * 60 * 60), vmax=vmax * CLIGHT
    )
