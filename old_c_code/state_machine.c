/**
 * @file state_machine.c
 * @author Juan J. Rojas
 * @date 7 Aug 2018
 * @brief State machine source file for Charge and Discharge System.
 * @par Institution:
 * LaSEINE / CeNT. Kyushu Institute of Technology.
 * @par Mail (after leaving Kyutech):
 * juan.rojas@tec.ac.cr
 * @par Git repository:
 * https://bitbucket.org/juanjorojash/cell_charger_discharger
 */

#include "charger_discharger.h"

/**@brief This function contain the transition definition for the states of the machine.
*/
void state_machine()
{
    switch(state){
    /**The #STANDBY  state goes to the #fSTANDBY()  function.*/
            case STANDBY:
                fSTANDBY();
                SECF = 1; //THis makes the thing go inside the state machine
                break;   
    /**The #IDLE  state goes to the #fIDLE()  function.*/             
            case IDLE:
                fIDLE();
                break;
    /**The #PREDISCHARGE  and #DISCHARGE  states go to the #fDISCHARGE()  function.*/ 
            case PREDISCHARGE:
            case DISCHARGE:
                fDISCHARGE();
                break;
    /**And the #POSTCHARGE  and #CHARGE  states go to the #fCHARGE()  function.*/  
            case POSTCHARGE:  
            case CHARGE:   
                fCHARGE();  
                break;
    /**The #CS_DC_res , #DS_DC_res  and #PS_DC_res  states go to the #fDC_res()  function.*/
            case CS_DC_res:
            case DS_DC_res:
            case PS_DC_res:
                fDC_res();
                break;
    /**The #WAIT  state goes to the #fWAIT()  function.*/
            case WAIT:    
                fWAIT();
                break;
    /**The #ISDONE  state goes to the #fISDONE()  function.*/
            case ISDONE:    
                fISDONE();
                break;
    /**The #FAULT  state goes to the #fFAULT()  function.*/
            case FAULT:    
                fFAULT();
                break;
    }
}

/**@brief This function define the #STANDBY  state of the state machine.
*/
void fSTANDBY()
{   
    STOP_CONVERTER(); /// * Stop the converter by calling the #STOP_CONVERTER() macro
    RCIE = 0; /// * Disable the USART reception interrupts to avoid interference with the setting of parameters in the #STANDBY state
    TMR1ON = 0; ///* Disable the Timer1 to avoid interference
    option = 0; /// * Initialize #option to 0
    cell_max = 0; /// * Initialize #cell_max to 0
    cell_count = '1'; /// * Initialize #cell_count to '1'
    LINEBREAK; 
    UART_send_string((char*)param_def_str); /// * Print message: <tt> ---Parameter definition for charger and discharger--- </tt>
    LINEBREAK;
    #if (LI_ION_CHEM) /// If #LI_ION_CHEM  is set to @b 1 and #NI_MH_CHEM  is set to @b 0, the folowing message will be displayed:
    UART_send_string((char*)chem_def_liion); /// * <tt> Chemistry defined as Li-Ion </tt>
    LINEBREAK;
    LINEBREAK;
    #elif (NI_MH_CHEM) /// If #NI_MH_CHEM  is set to @b 1 and #LI_ION_CHEM  is set to @b 0, the folowing message will be displayed:
    UART_send_string((char*)chem_def_nimh); /// * <tt> Chemistry defined as Ni-MH </tt>
    LINEBREAK;
    LINEBREAK; 
    #endif
    param(); /// Call the #param() function
}
/**@brief This function define the IDLE state of the state machine.
*/
void fIDLE()
{
    /**At first, the function will call the #Start_state_machine()  function.*/
    start_state_machine();
    /**Then, it will call the #Converter_settings()  function.*/
    converter_settings(); 
    /**Then, it will enable the USART reception interrupts to give the possibility to the user to press
    @b ESC to cancel or @b n to go to the next cell, at any time during the testing process*/            
    interrupt_enable();
}

/**@brief This function define the IDLE state of the state machine.
*/
void fCHARGE()
{
    LOG_ON(); /// * Activate the logging by calling #LOG_ON() macro
    conv = 1; /// * Activate control loop by setting #conv
    if (vavg < 900) //&& (qavg > 1)) /// If #vavg is below 0.9V
    {
        state = FAULT; /// * Go to #FAULT state
        UART_send_string((char*)cell_below_str); /// * Send a warning message
        LINEBREAK;
    }
    if (state == CHARGE){ /// If the #state is #CHARGE
        #if (LI_ION_CHEM) 
        /// If the chemistry is Li-Ion
        if ((iavg < EOC_current)  && (qavg > 100)) /// * If #iavg is below #EOC_current then
        {                
            prev_state = state; /// -# Set #prev_state equal to #state
            if (option == '3') state = ISDONE; /// -# If #option is '3' then go to #DONE state
            else state = WAIT; /// -# Else, go to #WAIT state
            wait_count = WAIT_TIME; /// -# Set #wait_count equal to #WAIT_TIME
            STOP_CONVERTER(); /// -# Stop the converter by calling #STOP_CONVERTER() macro
        }
        #elif (NI_MH_CHEM) 
        /// If the chemistry is Ni-MH
        if (((vavg < (vmax - Ni_MH_EOC_DV)) && (qavg > 100)) || minute >= timeout)
        {
            prev_state = state; /// -# Set #prev_state equal to #state
            if (option == '3') state = ISDONE; /// -# If #option is '3' then go to #ISDONE state
            else state = WAIT; /// -# Else, go to #WAIT state
            wait_count = WAIT_TIME; /// -# Set #wait_count equal to #WAIT_TIME
            STOP_CONVERTER(); /// -# Stop the converter by calling #STOP_CONVERTER() macro
        }
        #endif   
    } 
    if (state == POSTCHARGE){
        #if (LI_ION_CHEM) 
        if (qavg >= ( (capacity * 10) / 2 ) && ((minute + second) >= 1)){
            prev_state = state;
            state = WAIT;
            wait_count = WAIT_TIME;
            STOP_CONVERTER();
        #elif (NI_MH_CHEM)
        if (qavg >= ( (capacity * 10) / 2 ) || (unsigned) minute >= timeout){
            prev_state = state;
            state = WAIT;
            wait_count = WAIT_TIME;
            STOP_CONVERTER();
        }
        #endif  
    }    
}

/**@brief This function define the IDLE state of the state machine.
*/
void fDISCHARGE()
{
    LOG_ON(); /// * Activate the logging by calling #LOG_ON() macro
    conv = 1; /// * Activate control loop by setting #conv
    if (vavg < EOD_voltage) /// * If #vavg is below #EOD_voltage then
    {
        prev_state = state; /// -# Set #prev_state equal to #state
        if (option == '2'| option == '4') state = ISDONE; /// -# If #option is '2' or '4' then go to #ISDONE state
        else state = WAIT; /// -# Else, go to #WAIT state                  
        wait_count = WAIT_TIME; /// -# Set #wait_count equal to #WAIT_TIME
        STOP_CONVERTER(); /// -# Stop the converter by calling #STOP_CONVERTER() macro  
    }
}

/**@brief This function define the IDLE state of the state machine.
*/
void fDC_res() //can be improved a lot!!
{
    conv = 1; /// * Activate control loop by setting #conv
    if (dc_res_count == 4)  /// * If #dc_res_count is equal to 4 (CHANGE), then:
    {
        v_1_dcres = vavg;
        i_1_dcres = iavg;
        iref = (uint16_t) ( ( ( capacity * 4096.0 ) / (5000 * 2.5 * 1 ) ) + 0.5 );     //1C            
    }
    if (dc_res_count == 1)
    {
        v_2_dcres = vavg;
        i_2_dcres = iavg;
        STOP_CONVERTER();            
        dc_res_val = (uint24_t)(v_1_dcres - v_2_dcres) * 10000;    
        dc_res_val = dc_res_val /(uint24_t)(i_2_dcres - i_1_dcres);
    }
    if (!dc_res_count)
    {   
        LINEBREAK;
        UART_send_char(C_str);
        UART_send_char(cell_count);
        UART_send_char(comma);
        UART_send_char(S_str);
        display_value_u((uint16_t)state);
        UART_send_char(comma);
        UART_send_char(R_str);
        display_value_u((uint16_t)dc_res_val);
        UART_send_char('<');
        LINEBREAK;
        LOG_OFF();   ///I dont like this 
        prev_state = state;
        state = WAIT;
        wait_count = WAIT_TIME;              
    }else dc_res_count--;
}

/**@brief This function define the IDLE state of the state machine.
*/
void fWAIT()
{
    STOP_CONVERTER();  ///MAYBEOK
    if (wait_count)
    {   
        LINEBREAK;
        UART_send_char(C_str);
        UART_send_char(cell_count);
        UART_send_char(comma);
        UART_send_char(S_str);
        display_value_u((uint16_t)state);
        UART_send_char(comma);
        UART_send_char(W_str);
        display_value_u(wait_count);
        UART_send_char('<');
        wait_count--;             
    }
    if(!wait_count)
    {           
        switch(prev_state)
        {
            case PREDISCHARGE:
                state = CHARGE;
                converter_settings();
                break;
            case CHARGE:
                state = CS_DC_res; 
                converter_settings();
                break;
            case DISCHARGE:
                state = DS_DC_res; 
                converter_settings();
                break;
            case POSTCHARGE:
                state = PS_DC_res;
                converter_settings();
                break;
            case DS_DC_res:
                state = POSTCHARGE;
                converter_settings();
                break;
            case CS_DC_res:
                state = DISCHARGE;
                converter_settings();
                break;
            case PS_DC_res:
                state = ISDONE;
                STOP_CONVERTER();
                break;
        }
    }
}

/**@brief This function is executed every time a whole test process for one cell is finished
*/
void fISDONE()
{
    /**The function will check if the current cell number (@p cell_count) is smaller than the 
    number of cells to be tested (@p cell_max)*/
    if (cell_count < cell_max)
    {
        UART_send_string((char*)">END<");
        __delay_ms(500);
        /**If the condition is @b TRUE the counter will be incremented */       
        cell_count++;
        /**And the testin process of the next cell will be started by going to the @p IDLE state*/
        state = IDLE;   
    }else
    {
        UART_send_string((char*)">END<");
        state = STANDBY;
    }    
}

/**@brief This function define the FAULT state of the state machine.
*/
void fFAULT()
{   
    /**The function will stop the converter using #STOP_CONVERTER()  macro*/
    STOP_CONVERTER();
    /**The @p state will be set to @p STANDBY*/
    state = STANDBY;
}

/**@brief Function to start the state machine.
*/
void start_state_machine()
{
    /**First,*/
    switch(option)
    {
        /**Check the option (CHANGE)*/
        case '1':
            /**> if @option is equal to @b 1 it will set the @p state as @p PREDISCHARGE*/
            state = PREDISCHARGE;
            break;
        case '2':
            /**> if @option is equal to @b 2 it will set the @p state as @p CHARGE*/
            state = CHARGE;
            break;
        case '3':
            /**> if @option is equal to @b 3 it will set the @p state as @p CHARGE*/
            state = CHARGE;            
            break;
        case '4':
            /**> if @option is equal to @b 4 it will set the @p state as @p DISCHARGE*/
            state = DISCHARGE;                
            break;
    }
    /**First, this function will declare and initialized to zero a variable called @p start, which will
    be used to store the input of the user.*/ 
    unsigned char start = 0;
    switch (cell_count){
        /**If the current cell is the first (<tt>cell_count</tt>) , it will ask for user intervention to start.*/
        case '1':
            /**It will prompt the user to press @b s.*/
            UART_send_string((char*)press_s_str);
            LINEBREAK;                  
            while(start == 0)                                               
            {
                /**`The key pressed by the user will be assigned to @p start.*/
                start = UART_get_char();
                switch(start)
                {
                    /**If the user press @b s, the program will start.*/
                    case 's': 
                        break;
                    /**The user also can press @b ESC and the program will be restarted to the @p STANBY state.*/ 
                    case 0x1B:
                        state = STANDBY;
                        goto NOSTART;  //go to the end of the function 
                    /**If the user press something different from @b s, or @b ESC the program will print 
                    a warning message and wait for a valid input.*/
                    default:
                        LINEBREAK;
                        UART_send_string((char*)press_s_str);
                        LINEBREAK;
                        start = 0;  //Keep the program inside the while loop 
                        break;
                }
            }
            break;
        /**If the current cell is @b not @b '1' the program will start without 
        the user intervention.*/
        default: 
            break;
    }    
    /**Before starting, the program will print the following:*/
    LINEBREAK; 
    /**Starting...*/
    UART_send_string((char*)starting_str);                                            
    LINEBREAK; 
    LINEBREAK;
    /**Cell {1,2,3 or 4}*/
    UART_send_string((char*)cell_str);
    display_value_u((uint16_t)(cell_count - '0'));
    LINEBREAK; 
    NOSTART: ;  //label to goto the end of the function 
}

/**@brief Function to set the configurations of the converter.
*/
void converter_settings()
{
    kp = CC_kp; /// * The proportional constant, #kp is set to #CC_kp
    ki = CC_ki; /// * The proportional constant, #kp is set to #CC_kp
    cmode = 1; /// * Start in constant current mode by setting. #cmode
    intacum = 0; /// * The #integral component of the compensator is set to zero.*/
    qavg = 0; /// * Average capacity, #q_prom is set to zero.*/
    vmax = 0; /// * Maximum averaged voltage, #vmax is set to zero.*/
    dc = DC_MIN;
    set_DC();  /// * The #set_DC() function is called
    Cell_ON(); /// * The #Cell_ON() function is called
    switch(state)
    {
        case POSTCHARGE:
        case CHARGE: /// If the current state is @p POSTCHARGE or @p CHARGE
            iref = i_char; /// * The current setpoint, #iref is defined as #i_char
            timeout = ((capacity / ccref) * 66); /// * Charging #timeout is set to 10% more @b only_for}_NIMH
            SET_CHAR(); /// * The charge/discharge relay is set in charge position by calling the #SET_CHAR() macro
            break;
        case PREDISCHARGE:
        case DISCHARGE: /// If the current state is @p PREDISCHARGE or @p DISCHARGE
            iref = i_disc; /// * The current setpoint, #iref is defined as #i_disc
            SET_DISC(); /// * The charge/discharge relay is set in discharge position by calling the #SET_DISC() macro
            break;
        case CS_DC_res:
        case DS_DC_res:
        case PS_DC_res: /// If the current state is #CS_DC_res, #DS_DC_res or #PS_DC_res
            iref = (uint16_t) ( ( ( capacity * 4096.0 ) / (5000 * 2.5 * 5 ) ) + 0.5 ); /// * The current setpoint, #iref is defined as <tt> capacity / 5 </tt>
            dc_res_count = DC_RES_SECS; /// * The #dc_res_count is set to #DC_RES_SECS
            SET_DISC(); /// * The charge/discharge relay is set in discharge position by calling the #SET_DISC() macro
            break;
    }
    __delay_ms(10);   
}
/**@brief Function to define the parameters of the testing process for both chemistries.
*/
void param()
{
    /**First, this function will declare and intialize to zero a variable called @p input, which will
    be used to store the input of the user.*/
    unsigned char input = 0;
    /**Then, it will show the pre-set parameters for charging that are:*/
    /**For Li Ion:*/
    /**@code
    Li_Ion_CV = 4200 mV
    Li_Ion_CAP = 3250 mAh 
    @endcode*/ 
    /**For Ni_MH:*/
    /**@code
    Ni_MH_CV = 1700 mV //Just for protection for now, maybe is not necessary to show it
    Ni_MH_CAP = 2500 mAh
    @endcode*/
    LINEBREAK;  
    #if (LI_ION_CHEM)    
    cvref = (uint16_t) ( ( Li_Ion_CV * 4096 ) / 5000) + 0.5; //Scale the voltage refence to be compare with v
    cvv = Li_Ion_CV;
    UART_send_string((char*)cv_val_str);
    display_value_u(Li_Ion_CV);
    UART_send_string((char*)mV_str);
    LINEBREAK;
    /** The @p capacity will be set to @p Li_Ion_CAP.*/
    capacity = Li_Ion_CAP;
    UART_send_string((char*)nom_cap_str);
    display_value_u(capacity);
    UART_send_string((char*)mAh_str);
    #elif (NI_MH_CHEM) 
    vref = (uint16_t) ( ( ( Ni_MH_CV * 4096.0 ) / 5000 ) + 0.5 ); //Scale the voltage reference to be compare with v
    cvref = Ni_MH_CV;
    UART_send_string((char*)cv_val_str);
    display_value_u(Ni_MH_CV);
    UART_send_string((char*)mV_str);
    LINEBREAK;
    /** The @p capacity will be set to @p Ni_MH_CAP.*/
    capacity = Ni_MH_CAP;
    UART_send_string((char*)nom_cap_str);
    display_value_u(capacity);
    UART_send_string((char*)mAh_str);
    #endif
    LINEBREAK;
    LINEBREAK;    
    /**For the charging current it will print three options:*/
    UART_send_string((char*)def_char_curr_str);
    LINEBREAK;
    /** - 1) 0.25 C*/
    UART_send_string((char*)quarter_c_str);
    LINEBREAK;
    /** - 2) 0.5 C*/
    UART_send_string((char*)half_c_str);
    LINEBREAK;
    /** - 3) 1 C*/
    UART_send_string((char*)one_c_str);
    LINEBREAK;
    LINEBREAK;
    /** .*/
    while(input == 0)
    {
    /**The user should input the desired option.*/
        input = UART_get_char();  //Get the value in the terminal.
        switch(input)
        {   
            /**After chosing the charging current, the program will assign it to @p i_char and print it.*/
            case '1':
                i_char = (uint16_t) ( ( ( capacity * 4096.0 ) / (5000 * 2.5 * 4 ) ) + 0.5 );
                ccref = (uint16_t) ( (capacity / 4) + 0.5 );
                UART_send_string((char*)char_def_quarter_str);  //0.25C
                LINEBREAK;
                break;
            case '2':
                i_char = (uint16_t) ( ( ( capacity * 4096.0 ) / (5000 * 2.5 * 2 ) ) + 0.5 );
                ccref = (uint16_t) ( (capacity / 2) + 0.5 );
                UART_send_string((char*)char_def_half_str);  //0.5C
                LINEBREAK;
                break;
            case '3':
                i_char = (uint16_t) ( ( ( capacity * 4096.0 ) / (5000 * 2.5 * 1 ) ) + 0.5 );
                ccref = (uint16_t) ( (capacity / 1) + 0.5 );
                UART_send_string((char*)char_def_one_str);  //0.1C
                LINEBREAK;
                break;
                /**Unless the user press @e ESC, in that case the program will be restarted to the @p STANBY state.*/
                case 0x1B:
                state = STANDBY;
                LINEBREAK;
                UART_send_string((char*)restarting_str);  //restarting...
                LINEBREAK; 
                goto ESCAPE;  //go to the end of the function 
                /**If the user press something different from @b 1, @b 2, @b 3 or @b ESC the program will print 
                a warning message and wait for a valid input.*/
                default:
                input = 0;  //stay inside the while loop.
                LINEBREAK;
                UART_send_string((char*)num_1and3_str);  //ask the user to use a number between 1 and 3.
                LINEBREAK;                
                break;
        }
    }
    /**Variable @p input is cleared*/
    input = 0; 
    /**Next, the program will show the end-of-charge parameters that are:*/
    /**For Li Ion, the end-of-charge current:*/
    /**@code
    Li_Ion_EOC_I = 100 mA
    @endcode*/ 
    /**For Ni_MH, the end-of-charge voltage drop:*/
    /**@code
    Ni_MH_EOC_DV = 10 mV
    @endcode*/
    #if (LI_ION_CHEM)
    EOC_current = Li_Ion_EOC_I;
    UART_send_string((char*)EOC_I_str);
    display_value(EOC_current);
    UART_send_string((char*)mA_str);
    #elif (NI_MH_CHEM) 
    UART_send_string((char*)EOC_DV_str);
    display_value_u(Ni_MH_EOC_DV);
    UART_send_string((char*)mV_str);
    #endif    
    LINEBREAK; 
    LINEBREAK;
    /**For the discharging current it will show three options:*/
    UART_send_string((char*)def_disc_curr_str);
    LINEBREAK;
    /** - 1) 0.25 C*/
    UART_send_string((char*)quarter_c_str);
    LINEBREAK;
    /** - 2) 0.5 C*/
    UART_send_string((char*)half_c_str);
    LINEBREAK;
    /** - 3) 1 C*/
    UART_send_string((char*)one_c_str);
    LINEBREAK;
    LINEBREAK;
    /** .*/
    while(input == 0)
    {
        /**The user should input the desired option.*/
        input = UART_get_char();  //Get the value in the terminal.
        switch (input)
        {
            /**After chosing the discharging current, the program will assign it to @p i_disc and print it.*/
            case '1':
                i_disc = (uint16_t) ( ( ( capacity * 4096.0) / ( 5000 * 2.5 * 4 ) ) + 0.5 );
                UART_send_string((char*)dis_def_quarter_str);  //0.25 C
                LINEBREAK;            
                break;
            case '2':
                i_disc = (uint16_t) ( ( ( capacity * 4096.0 ) / ( 5000 * 2.5 * 2 ) ) + 0.5 );
                UART_send_string((char*)dis_def_half_str);  //0.5 C
                LINEBREAK;         
                break;
            case '3':
                i_disc = (uint16_t) ( ( ( capacity * 4096.0 ) / ( 5000 * 2.5 * 1 ) ) + 0.5 );
                UART_send_string((char*)dis_def_one_str);  //1C
                LINEBREAK;
                break;
            /**Unless the user press @e ESC, in that case the program will be restarted to the @p STANBY state.*/
            case 0x1B:  //ESC button was pressed
                state = STANDBY;
                LINEBREAK;
                UART_send_string((char*)restarting_str);  //restarting...
                LINEBREAK;             
                goto ESCAPE;  //go to the end of the function 
            /**If the user press something different from @e 1, @e 2, @e 3 or @e ESC the program will print 
            a warning message and wait for a valid input.*/
            default:
                input = 0;
                LINEBREAK;
                UART_send_string((char*)num_1and3_str);  //ask the user to use a number between 1 and 3.
                LINEBREAK;                
                break;
        }
    }
    /**Varible @p input is cleared*/
    input = 0;
    /**Next, the program will show the end-of-discharge voltage constant that is: ((CHANGE THIS STYLE))*/
    /**For Li Ion:*/
    /**@code
    Li_Ion_EOD_V = 3000 mV
    @endcode*/ 
    /**For Ni_MH:*/
    /**@code
    Ni_MH_EOD_V = 1000 mV
    @endcode*/
    #if (LI_ION_CHEM)
    EOD_voltage = Li_Ion_EOD_V;
    UART_send_string((char*)EOD_V_str);
    #elif (NI_MH_CHEM)
    EOD_voltage = Ni_MH_EOD_V;  //This is compared to vavg
    UART_send_string((char*)EOD_V_str);
    #endif
    display_value_u(EOD_voltage);
    UART_send_string((char*)mV_str);
    LINEBREAK;
    /**For the test cycle it will show four options:*/
    LINEBREAK;
    UART_send_string((char*)cho_bet_str);
    LINEBREAK;
    /** - 1) Precharge->Discharge->Charge (includes DC resistance measure after charge and after discharge).*/
    UART_send_string((char*)op_1_str);
    LINEBREAK;
    /** - 2) Discharge->Charge (includes DC resistance measure after charge and after discharge).*/
    UART_send_string((char*)op_2_str);
    LINEBREAK;
    /** - 3) Only Charge*/
    UART_send_string((char*)op_3_str);
    LINEBREAK;
    /** - 4) Only Discharge*/
    UART_send_string((char*)op_4_str);
    LINEBREAK;
    LINEBREAK;
    /** .*/
    while(option == 0)
    {
        /**The user should input the desired option, which will be assigned to @p option*/
        option = UART_get_char();  //Get the value in the terminal.
        switch(option)
        {
            /**After that the program will print the selected option and:*/
            case '1':
                LINEBREAK;
                UART_send_string((char*)op_1_sel_str);  //Predischarge->Charge->Discharge->Postcharge
                LINEBREAK;
                break;
            case '2':
                LINEBREAK;
                UART_send_string((char*)op_2_sel_str);  //Charge->Discharge
                LINEBREAK;
                break;
            case '3':
                LINEBREAK;
                UART_send_string((char*)op_3_sel_str);  //Only Charge
                LINEBREAK;         
                break;
            case '4':
                LINEBREAK;
                UART_send_string((char*)op_4_sel_str);  //Only Discharge
                LINEBREAK;             
                break;
            /**Unless the user press @e ESC, in that case the program will be restarted to the @p STANBY state.*/
            case 0x1B:
                state = STANDBY;
                LINEBREAK;
                UART_send_string((char*)restarting_str);
                LINEBREAK;
                goto ESCAPE;  //go to the end of the function 
            /**If the user press something different from @b 1, @b 2, @b 3, @b 4 or @b ESC the program will print 
            a warning message and wait for a valid input.*/
            default:
                option = 0;
                LINEBREAK;
                UART_send_string((char*)num_1and4_str);  //ask the user to use a number between 1 and 4.
                LINEBREAK;
                break;
        }
    }
    LINEBREAK;
    /**Then, the program will ask the user how many cells he wants to test (4 cells is the maximum):*/
    UART_send_string((char*)def_num_cell_str);
    LINEBREAK;
    while(cell_max == 0)
    {
        /**The user should input the desired number, which will be assigned to @p cell_max*/
        cell_max = UART_get_char();  //Get the value in the terminal.
        switch(cell_max)
        {
            /**After that the program will print it.*/
            case '1':
                LINEBREAK;
                UART_send_string((char*)num_cell_str);
                UART_send_string((char*)one_str);
                LINEBREAK;
                break;
            case '2':
                LINEBREAK;
                UART_send_string((char*)num_cell_str);
                UART_send_string((char*)two_str);
                LINEBREAK;
                break;
            case '3':
                LINEBREAK;
                UART_send_string((char*)num_cell_str);
                UART_send_string((char*)three_str);
                LINEBREAK;  
                break;
            case '4':
                LINEBREAK;
                UART_send_string((char*)num_cell_str);
                UART_send_string((char*)four_str);
                LINEBREAK;
                break;
            /**Unless the user press @b ESC, in that case the program will be restarted to the @p STANBY state.*/
            case 0x1B:
                state = STANDBY;
                LINEBREAK;
                UART_send_string((char*)restarting_str);
                LINEBREAK;
                goto ESCAPE;  //go to the end of the function 
            /**If the user press something different from @b 1, @b 2, @b 3, @b 4 or @b ESC the program will print 
            a warning message and wait for a valid input.*/
            default:
                cell_max = 0;   //Keep the program inside the while loop 
                LINEBREAK;
                UART_send_string((char*)num_1and4_str);  //ask the user to use a number between 1 and 4.
                LINEBREAK;
                break;
        }           
    }
    /**After the user has set the number of cells the program will go to the @p IDLE state. @see fIDLE()*/
    state = IDLE;  //go to IDLE state
    ESCAPE: ;  //label to goto the end of the function 
}