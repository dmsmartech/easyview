[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/dmsmartech/easyview)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

# Medtrum EasyView — Home Assistant Integration

🇬🇧 English | [🇮🇹 Italiano](README_IT.md) | [🇷🇺 Русский](README_RU.md)

---

This integration allows you to display real-time CGM (Continuous Glucose Monitor) data from **Medtrum** sensors in Home Assistant, read via the **EasyView** cloud.

---

## How it works

The Medtrum CGM sensor transmits data to the **EasyView** app on the patient's phone. Via the Follow sharing feature, this data is sent to the cloud and made available to a second account through the **EasyView Follow** function.

The Home Assistant integration connects to this Follow account to read the data in real time.

---

## Prerequisites

- An active Medtrum CGM sensor
- The **EasyView** app installed on the patient's phone, with a registered Medtrum account
- A **second Medtrum account** to use as a Follow account (can be a secondary account of yours)
- Home Assistant with HACS installed

---

## Step 1 — Invite the Follow account from EasyView

On the patient's phone, in the **EasyView** app:

1. Open the app and go to **Settings**
2. Select **Follow** or **Sharing**
3. Enter the email address of the second account
4. Send the invitation

---

## Step 2 — Accept the invitation and verify access

On the device where you received the invitation:

1. Accept the invitation via the received email or notification
2. Log in to the EasyView Follow account
3. Verify that the patient's glucose data is visible

---

## Step 3 — Install the integration in Home Assistant

### Via HACS

1. Open HACS in Home Assistant
2. Go to **Integrations** → click the three dots in the top right → **Custom repositories**
3. Enter the repository URL: `https://github.com/dmsmartech/easyview`
4. Select the category **Integration**
5. Click **Add**
6. Search for **EasyView** in HACS and install it
7. Restart Home Assistant

### Manual installation

1. Copy the `custom_components/easyview` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant

---

## Step 4 — Configure the integration

1. In Home Assistant go to **Settings** → **Devices & services**
2. Click **Add integration** and search for **EasyView**
3. Enter:
   - **Email** and **Password** of the EasyView Follow account
   - **Unit of measurement** — `mg/dL` or `mmol/L`
   - **High glucose threshold** — value above which the *Is High* sensor activates (default: 180 mg/dL)
   - **Low glucose threshold** — value below which the *Is Low* sensor activates (default: 70 mg/dL)
4. Click **Submit**

If the credentials are correct, the integration will connect and the sensors will be created automatically.

---

## Available sensors

For each monitored user, the following are created:

| Sensor | Description |
|---|---|
| Glucose | Current value in mg/dL or mmol/L |
| Glucose Trend | Text + icon (Stable, Increasing, Decreasing, etc.) |
| Sensor Status | Normal / Warming up / Needs calibration |
| Battery | Sensor battery percentage |
| Minutes since update | Minutes since the last sensor reading |
| Is High | On / Off (configurable threshold) |
| Is Low | On / Off (configurable threshold) |

---

## Modifying alert thresholds

Thresholds can be changed at any time without reinstalling:

1. In Home Assistant go to **Settings** → **Devices & services**
2. Find the **EasyView** integration and click the ✏️ **Configure** icon
3. Update the **High glucose threshold** and/or **Low glucose threshold**
4. Click **Submit**

---

## Re-authentication

If the integration stops working due to an expired session:

1. In Home Assistant go to **Settings** → **Devices & services**
2. You will see a notification on the EasyView integration — click **Re-authenticate**
3. Re-enter your credentials

There is no need to remove and reinstall the integration.

---

## Common issues

| Issue | Solution |
|---|---|
| Authentication error | Check the email and password of the Follow account |
| No data visible | Verify that the invitation has been accepted and data is visible in the Follow account |
| Sensors unavailable | Check internet connectivity and restart the integration |
| Battery shows wrong value | Update to the latest version of the integration |

---

## Credits

Developed by [dmsmartech](https://github.com/dmsmartech).  
API usage based on the open source project [nl-ruud/nightscout-easyview](https://github.com/nl-ruud/nightscout-easyview).
