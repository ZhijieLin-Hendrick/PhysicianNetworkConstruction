# Physician Social Network Construction

### 1. Source Data
-   National Downloadable File: https://data.cms.gov/provider-data/dataset/mj5m-pzi6
    -   I used the data downloaded on 2022 April, but that one have been updated and is not available on the official website
    -   Therefore, all of the analysis below is based on the data of 2022 April

### 2. Network Construction
- Based on the data preprocess by ```data_utils.data_preprocess``` and ```data_utils.data_split```, we could build a physician social network with at least 2 common hospitals and at least 1 common specialties, of which the log-log plot is close to linear one.
- ![image](./Graph%20with%20edge%20with%20at%20least%201%20common%20spec%20and%20at%20least%202%20common%20hosp%20.png)
- The data of physician social network with at least 2 common hospitals and at least 1 common specialties is stored in ```./data/diff_hosp_weight/hosp_edgeWeight_2```



