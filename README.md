# Insnrg custom integration

![GitHub Release](https://img.shields.io/github/release/jaringuyen/InsnrgHomeAssistance.svg?style=plastic) ![GitHub issues](https://img.shields.io/github/issues/jaringuyen/InsnrgHomeAssistance.svg?style=plastic) ![GitHub Stars](https://img.shields.io/github/stars/jaringuyen/InsnrgHomeAssistance.svg?style=plastic) ![GitHub Last Commit](https://img.shields.io/github/last-commit/jaringuyen/InsnrgHomeAssistance.svg?style=plastic) ![Documentation](https://img.shields.io/badge/docs-excellent-brightgreen.svg?style=plastic) ![HACS Status](https://img.shields.io/badge/HACS-Default-blue.svg?style=plastic) ![Home Assistant](https://img.shields.io/badge/Home%20Assistant-%3E%3D%202024.10.1-brightgreen.svg?style=plastic)

<p align="center">
  <img src="https://github.com/user-attachments/assets/8e05446e-bc14-4a21-9f6d-8e9f9defd630" alt="Image">
</p>

<p align="center">
 <img src="https://github.com/user-attachments/assets/4b954930-9611-4408-a047-09a35a6e01cc" alt="Image">
</p>

The Insnrg custom integration sets up 40 sensors:

- **SPA**
- **Filter Mode**
- **All Auto**
- **Set Spa Temperature**
- **Set Pool Temperature**
- **Current pH**
- **Set Point pH**
- **Current ORP**
- **Set Point ORP**
- **pH Connected**
- **ORP Connected**
- **Pool Current Temperature**
- **Outlet data for each of the 3 Vi-Outlets and 4 Hub-Outlets**:
  - Waterfall, Jet Pump, Lights, In Floor, Ozone, Blower
- **Valve data for each of the 3 Vi-Valves and 4 Hub-Valves**
  - Waterfall, Feature
- **Timer data for each of the 4 timers**:
  - Chlorinator
  - Enabled
- **VF Contact data for each of the 1 Vi-VF Contact and 3 Hub-VF Contacts**:
  - Heat Pump, Gas
- **Pump Speed**
- **Chlorinator**

---

## **Installing the Insnrg Custom Integration in Home Assistant via HACS**

This guide will walk you through the steps to install and set up the Insnrg custom integration in Home Assistant via the Home Assistant Community Store (HACS).

### **Prerequisites**

- **Home Assistant** must already be installed and configured on your system.
- **HACS** should be installed. If not, follow the instructions at [HACS Installation](https://www.hacs.xyz/docs/use/download/prerequisites/).
- NOTES: Please contact insnrgdev@insnrg.com to request access to Insnrg 3rd Party REST API, and enable Voice Control in Connected Systems screen.

### **Step-by-Step Guide**

#### **1. Open HACS**

- In Home Assistant, navigate to the side menu and click on **"HACS"**.

#### **2. Add Custom Repository**

- Click on the **three dots menu** at the top right in HACS.
- Select **"Custom Repositories"**.

#### **3. Add Repository**

- In the **"Add Custom Repository URL"** field, paste the following URL:
  ```
  https://github.com/jaringuyen/InsnrgHomeAssistance
  ```
- Under **"Category"**, select **"Integration"**.
- Click on **"Add"**.

#### **4. Install Integration**

- After adding, the integration should be available in HACS.
- Search for **"insnrg"** in the HACS integrations list.
- Click on the integration and then click **"Install this repository"**.
- Confirm the installation by clicking **"Install"**.

#### **5. Restart Home Assistant**

- After installation, you need to restart Home Assistant to load the integration.
- Go to **"Settings" > "System" > "Restart"** and click on **"Restart"**.

#### **6. Set Up Integration**

- After the restart, navigate to **"Settings" > "Devices & Services"**.
- Click on **"Add Integration"** (the **"+"** symbol at the bottom right).
- Search for **"insnrg"**.
- Select the integration from the list.

#### **7. Enter Credentials**

- Enter your **email address** and **password** that you use to log in to [https://www.insnrgapp.com](https://www.insnrgapp.com).
- Click **"Submit"** or **"Next"** to complete the setup.

#### **8. Verify Installation**

- After successful setup, the sensors for your chlorinator will be created.
- You can view them under **"Settings" > "Devices & Services"**.
- Add the desired sensors to your dashboard to display the data.

## **Notes**

If you have any issues with Insnrg entities, please try to Reload the integration.
To reload a HACS integration in Home Assistant, follow these steps:

- Open Home Assistant and go to Settings > Devices & Services.
- Find the integration you want to reload.
- Click on the three-dot menu (⋮) next to the integration.
- Select Reload from the menu.
- If the integration doesn't support reloading, you might need to restart Home Assistant.
