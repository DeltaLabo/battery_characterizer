/**
 * @file charger_discharger.c
 * @author Juan J. Rojas
 * @date 7 Aug 2018
 * @brief Hardware related functions source file.
 * @par Institution:
 * LaSEINE / CeNT. Kyushu Institute of Technology.
 * @par Mail (after leaving Kyutech):
 * juan.rojas@tec.ac.cr
 * @par Git repository:
 * https://bitbucket.org/juanjorojash/cell_charger_discharger
 */

#include "charger_discharger.h"

/**@brief Function to initialize all the PIC16F1787 registers
*/
void initialize()
{
    /** <b> GENERAL </b>*/
    CLRWDT(); /// * Clear WDT by calling @p CLRWDT()
    nWPUEN = 0; /// * Allow change of individual WPU
    WPUE3 = 1;      //Enable pull up for MCLR
    /** <b> SYSTEM CLOCK </b>*/
    OSCCONbits.IRCF = 0b1111; /// * Set clock to 32MHz (PLL is enabled)
    OSCCONbits.SCS = 0b00; /// * Clock determined by FOSC<2:0> in Configuration Words
    OSCCONbits.SPLLEN = 1; /// * Enable PLL. 
    //According to errata this shall not be done in the Configuration Words
    /** <b> RELAY OUPUTS </b> */
    //PORTC doesn't have ANSELC
    TRISC3 = 0; /// * Set RC3 as output. Set for discharge
    WPUC3 = 0; /// * Deactivate weak pull up in RC3
    TRISC4 = 0; /// * Set RC4 as output. Set for charge
    WPUC4 = 0; /// * Deactivate weak pull up in RC4    
    TRISC5 = 0; /// * Set RC5 as output. ON/OFF relay
    WPUC5 = 0; /// * Deactivate weak pull up in RC5
    /** <b> CELL SWITCHER OUPUTS </b>*/
    TRISB2 = 0; /// * Set RB2 as output. Set for Cell #1
    ANSB2 = 0; /// * Set RB2 as digital
    WPUB2 = 0; /// * Deactivate weak pull up in RB2
    TRISB3 = 0; /// * Set RB3 as output. Set for Cell #2
    ANSB3 = 0; /// * Set RB3 as digital
    WPUB3 = 0; /// * Deactivate weak pull up in RB3
    TRISB4 = 0; /// * Set RB4 as output. Set for Cell #3
    ANSB4 = 0; /// * Set RB4 as digital  
    WPUB4 = 0; /// * Deactivate weak pull up in RB4
    TRISB5 = 0; /// * Set RB5 as output. Set for Cell #4
    ANSB5 = 0; /// * Set RB5 as digital  
    WPUB5 = 0; /// * Deactivate weak pull up in RB5
    Cell_OFF();
    /** @b TIMER1 */
    nT1SYNC = 0; /// * Synchronize asynchronous clock input with system clock (FOSC)
    T1OSCEN = 0; /// * Dedicated Timer1 oscillator circuit disabled    
    TMR1ON = 0; /// * Enables Timer1
    TMR1GE = 0; /// * Timer1 counts regardless of Timer1 gate function
    TMR1CS0 = 0; // TMR1CS=0b00      
    TMR1CS1 = 0; /// * Timer1 clock source is instruction clock (FOSC/4)
    T1CKPS0 = 0; // T1CKPS=0b00  
    T1CKPS1 = 0; /// * 1:1 Prescale value
    TMR1H = 0xE1; //TMR1 Fosc/4= 8Mhz (Tosc= 0.125us). TMR1 counts: 7805 x 0.125us = 0.97562 ms
    TMR1L = 0x83; /// * Set Timer1 register to overflow in 0.97562 ms
    /** <b> PROGRAMMABLE SWITCH MODE CONTROL (PSMC) </b> */
    PSMC1CON = 0x00; /// * Clear PSMC1 configuration
    PSMC1MDL = 0x00; /// * No modulation
    PSMC1CLK = 0x01; /// * Driven by 64MHz PLL system clock
    PSMC1PRH = 0x01; //
    PSMC1PRL = 0xFF; /// * Set period register to overflow in 8us (125kHz)
    // 511 + 1 clock cycles for period that is 8us (125kHz)
    // This set the PWM with 9 bit of resolution
    PSMC1DCH = 0x00;    //   
    PSMC1DCL = 0x32;    // * Set duty cycle register to a 10% duty cycle (0x0032)
    PSMC1PHH = 0x00; 
    PSMC1PHL = 0x00; /// * Rising event starts from the beginning, i.e duty cycle is in-phase with the period
    P1STRC = 1; /// * Single PWM activated in PSMC1C (RC2)
    P1POLC = 0; /// * PWM PSMC1 output is active-high (RC2)
    P1OEC = 1; /// * PSMC output is active in PSMC1C (RC2)
    P1PRST = 1; /// * Period event occurs when PSMC1TMR = PSMC1PR
    P1PHST = 1; /// * Rising edge event occurs when PSMC1TMR = PSMC1PH
    P1DCST = 1; /// * Falling edge event occurs when PSMC1TMR = PSMC1DC
    PSMC1CON = 0x80; /// * PSMC1 module is enable
    /// * Disable buffer load
    /// * Disable dead band
    /// * Operating mode: Single PWM
    TRISC2 = 0; /// * Set RC2 as output. PWM output
    WPUC2 = 0; /// * Deactivate weak pull up in RC2    
    /** @b ADC*/
    TRISA3 = 1; /// * Set RA3 as input. VREF+
    ANSA3 = 1; /// * Set RA3 as analog
    WPUA3 = 0; /// * Deactivate weak pull up in RA3
    TRISB1 = 1; /// * Set RB1 as input. Voltage sense
    ANSB1 = 1; /// * Set RB1 as analog
    WPUB1 = 0; /// * Deactivate weak pull up in RB1
    TRISB0 = 1; /// * Set RB0 as input. Current sense
    ANSB0 = 1; /// * Set RB0 as analog
    WPUB0 = 0; /// * Deactivate weak pull up in RB0
    TRISA5 = 1; /// * Set RA5 as input. Temperature sense
    ANSA5 = 1; /// * Set RA5 as analog
    WPUA5 = 0; /// * Deactivate weak pull up in RA5
    ADCON0bits.ADRMD = 0; /// * 12-bit result
    ADCON1bits.ADCS = 0b010; /// * Clock selected as FOSC/32
    ADCON1bits.ADNREF = 0; /// * Negative reference connected to VSS
    ADCON1bits.ADPREF = 0b01; /// * Positive reference connected to VREF+
    ADCON1bits.ADFM = 1; /// * 2's compliment result
    ADCON2bits.CHSN = 0b1111; /// * Negative differential input given by ADNREF
    ADCON0bits.ADON = 1; /// * ADC is enabled
    /** @b UART*/
    TXSEL = 0; /// * RC6 selected as TX
    RXSEL = 0; /// * RC7 selected as RX
    SP1BRGH = 0x00; 
    SP1BRGL = 0x8A; // * Baud rate register set to 57600 bps    
    BRGH  = 1;  /// * High baud rate set
    BRG16 = 1;  /// * 16-bit timer set
    SYNC  = 0;  /// * Asynchronous serial
    SPEN  = 1;  /// * Enable serial port pins
    TXEN  = 1;  /// * Enable transmission
    CREN  = 1;  /// * Enable reception
    TX9   = 0;  /// * 8-bit transmission selected
    RX9   = 0;  /// * 8-bit reception selected
    RCIE = 0; /// * Disable UART reception interrupts
    TXIE = 0; /// * Disable UART transmission interrupts
    /** @b FINAL */
    STOP_CONVERTER(); ///* Call #STOP_CONVERTER() macro
}
/**@brief This function calls the PI control loop for current or voltage depending on the value of the #cmode variable.
*/
void control_loop()
{   
    if(!cmode) /// If #cmode is cleared then
    {
        pid(v, vref);  /// * The #pid() function is called with @p feedback = #v and @p setpoint = #vref
    }else /// Else,
    {
        pid(i, iref); /// * The #pid() function is called with @p feedback = #i and @p setpoint = #iref
    }
    set_DC(); /// The duty cycle is set by calling the #set_DC() function
}
/**@brief This function defines the PI controller
*  @param   feedback average of measured values for the control variable
*  @param   setpoint desire controlled output for the variable
*/
void pid(uint16_t feedback, uint16_t setpoint) 
{ 
int16_t     er = 0; 
int16_t     pi = 0; 
int16_t     prop = 0; 
int16_t     inte = 0;
    /// This function performs the folowing tasks:
    er = (int16_t) (setpoint - feedback); /// <ol> <li> Calculate the error
    if(er > ERR_MAX) er = ERR_MAX; /// <li> Make sure error is never above #ERR_MAX
    if(er < ERR_MIN) er = ERR_MIN; /// <li> Make sure error is never below #ERR_MIN
    prop = er / kp; /// <li> Calculate the proportional component of compensator
	intacum += (int24_t) (er); 
    inte = (int16_t) (intacum / ((int24_t) ki * COUNTER)); /// <li> Calculate the integral component of compensator usign #intacum to accumulate over cycles
    pi = prop + inte; /// <li> Combine proportinal and integral parts
    dc = (uint16_t)((int16_t)dc + pi);/// <li> Sum the result to the previous duty cycle stored in the #dc variable
    if (dc >= DC_MAX){ /// <li> Make sure the duty cycle is never above #DC_MAX
        dc = DC_MAX;
    }else if (dc <= DC_MIN){ /// <li> Make sure duty cycle is never below #DC_MIN </ol>
        dc = DC_MIN;
    }
}
/**@brief This function sets the desired duty cycle of the PWM
*/
void set_DC() /// This function performs the folowing tasks:
{
    PSMC1DCL = dc & 0x00FF; 
    PSMC1DCH = (dc >> 8) & 0x01; /// <ol> <li> Load the duty cycle register of the PSMC with the #dc variable
    PSMC1CONbits.PSMC1LD = 1; /// <li> Set the load register. This will load all the setting at once </ol>
}
/**@brief This function switches between CC and CV mode.
* @param current_voltage average of current voltage
* @param referece_voltage voltage setpoint
* @param CC_mode_status current condition of #cmode variable
*/
void cc_cv_mode(uint16_t current_voltage, uint16_t reference_voltage, bool CC_mode_status)
{
/// If the current voltage is bigger than the CV setpoint and the system is in CC mode, then:
    if(current_voltage > reference_voltage && CC_mode_status)
    {        
            intacum = 0; /// <ol> <li> The integral acummulator is cleared
            cmode = 0; /// <li> The system is set in CV mode by clearing the #cmode variable
            kp = CV_kp; /// <li> The proportional constant divider is set to #CV_kp 
            ki = CV_ki; /// <li> The integral constant divider is set to #CV_ki 
    }    
}
/**@brief This function takes care of scaling the average values to correspond with their real values.
*/
void scaling() /// This function performs the folowing tasks:
{
iavg = (uint16_t) ( ( ( iavg * 2.5 * 5000 ) / 4096 ) + 0.5 ); /// <ol><li> Scale #iavg according to the 12-bit ADC resolution (4096) and the sensitivity of the sensor (0.4 V/A). 
vavg = (uint16_t) ( ( ( vavg * 5000.0 ) / 4096 ) + 0.5 ); /// <li> Scale #vavg according to the 12-bit ADC resolution (4096)
tavg = (uint16_t) ( ( ( tavg * 5000.0 ) / 4096 ) + 0.5 ); 
tavg = (int16_t) ( ( ( 1866.3 - tavg ) / 1.169 ) + 0.5 ); /// <li> Scale #tavg according to the 12-bit ADC resolution (4096) and the sensitivity of the sensor ( (1866.3 - x)/1.169 )
qavg += (uint16_t) ( iavg / 360 ) + 0.5; /// <li> Perform the discrete integration of #iavg over one second and accumulate in #qavg 
#if (NI_MH_CHEM)  
if (vavg > vmax) vmax = vavg; /// <li> If the chemistry is Ni-MH and #vavg is bigger than #vmax then set #vmax equal to #vavg
#endif
}
/**@brief This function takes care of calculating the average values printing the log data using the UART.
*/
void log_control()
{
    if (log_on)
    {
                LINEBREAK;
                display_value_u(minute);
                UART_send_char(colons); /// * Send a colons character
                if (second < 10) UART_send_char('0'); /// * If #second is smaller than 10 send a '0'
                display_value_u((uint16_t) second);
                UART_send_char(comma); /// * Send a comma character
                UART_send_char(C_str); /// * Send a 'C'
                UART_send_char(cell_count); /// * Send a #cell_count variable
                UART_send_char(comma); /// * Send a comma character
                UART_send_char(S_str); /// * Send an 'S'
                display_value_u((uint16_t)state);
                UART_send_char(comma); /// * Send a comma character
                UART_send_char(V_str); /// * Send a 'V'
                display_value_u(vavg);
                UART_send_char(comma); ///* Send a comma character
                UART_send_char(I_str); /// * Send an 'I'
                display_value_u(iavg);
                UART_send_char(comma); ///* Send a comma character
                UART_send_char(T_str); /// * Send a 'T'
                display_value_s(tavg);
                UART_send_char(comma); ///* Send a comma character
                UART_send_char(Q_str); /// * Send a 'Q'
                //display_value_u((uint16_t) (dc * 1.933125));
                display_value_u(qavg);
                UART_send_char('<'); /// * Send a '<'
    }
    if (!log_on) RESET_TIME(); /// If #log_on is cleared, call #RESET_TIME()
}

/**@brief This function read the ADC and store the data in the coresponding variable
*/
uint16_t read_ADC(uint16_t channel)
{
    uint16_t ad_res = 0;
    __delay_us(10);
    ADCON0bits.CHS = channel;
    __delay_us(10);
    GO_nDONE = 1;
    while(GO_nDONE);
    ad_res = (uint16_t)((ADRESL & 0xFF)|((ADRESH << 8) & 0xF00));
    return ad_res;
}

/**@brief This function control the timing
*/
void timing()
{
    if(!count) /// If #count is other than zero, then
    {
        SECF = 1;
        count = COUNTER + 1; /// * Make #count equal to #COUNTER
        if(second < 59) second++; /// * If #second is smaller than 59 then increase it
        else{second = 0; minute++;} /// * Else, make #second zero and increase #minute
    }else /// Else,
    {
        count--; /// * Decrease it
    }
}
/**@brief This function calculate the averages
*/
void calculate_avg()
{
    switch(count)
    {
        case COUNTER + 1: /// If #count = #COUNTER
            iacum = 0; /// * Make #iavg zero
            vacum = 0; /// * Make #vavg zero
            tacum = 0; /// * Make #tavg zero
            break;
        case 0: /// If #count = 0
            iavg = ((iacum >> 10) + ((iacum >> 9) & 0x01)); /// * Divide the value stored in #iavg between COUNTER to obtain the average   
            vavg = ((vacum >> 10) + ((vacum >> 9) & 0x01)); /// * This is equivalent to vacum / 1024 = vacum / 2^10 
            tavg = ((tacum >> 10) + ((tacum >> 9) & 0x01)); /// * This is equivalent to tacum / 1024 = tacum / 2^10 
            break;
        default: /// If #count is not any of the previous cases then
            iacum += (uint24_t) i; /// * Accumulate #i in #iavg
            vacum += (uint24_t) v; /// * Accumulate #v in #vavg
            tacum += (uint24_t) t; /// * Accumulate #t in #tavg
            //tavg += dc * 1.953125; // TEST FOR DC Is required to deactivate temperature protection
    }   
}
/**@brief This function activate the UART reception interruption 
*/
void interrupt_enable()
{
    char clear_buffer = 0; /// * Define the variable @p clear_buffer, used to empty the UART buffer
    while(RCIF){
        clear_buffer = RC1REG; /// * Clear the reception buffer and store it in @p clear_buffer
    }
    RCIE = 1; /// * Enable UART reception interrupts
    TXIE = 0; /// * Disable UART transmission interrupts
    TMR1IE = 1;   //enable T1 interrupt
    PEIE = 1;       //enable peripherals interrupts
    GIE = 1;        //enable global interrupts
    count = COUNTER + 1; /// The timing counter #count will be initialized to zero, to start a full control loop cycle
    TMR1IF = 0; //Clear timer1 interrupt flag
    TMR1ON = 1;    //turn on timer 
}
/**@brief This function send one byte of data to UART
* @param bt character to be send
*/
void UART_send_char(char bt)  
{
    while(0 == TXIF)
    {
    }/// * Hold the program until the transmission buffer is free
    TX1REG = bt; /// * Load the transmission buffer with @p bt
}
/**@brief This function receive one byte of data from UART
* @return RC1REG reception register
*/
char UART_get_char()
{
    if(OERR) /// If there is error
    {
        CREN = 0; /// * Clear the error
        CREN = 1; /// * Restart
    }    
    while(!RCIF);  /// Hold the program until the reception buffer is free   
    return RC1REG; /// Receive the value and return it
}
/**@brief This function send a string using UART
* @param st_pt pointer to string to be send
*/
void UART_send_string(char* st_pt)
{
    while(*st_pt) /// While there is a byte to send
        UART_send_char(*st_pt++); /// * Send it using #UART_send_char() and then increase the pointer possition
}
///**@brief This function convert a number to string and then send it using UART
//* @param value integer to be send
//*/
void display_value_u(uint16_t value)
{   
    char buffer[6]; /// * Define @p buffer to used it for store character storage
    utoa(buffer,value,10);  /// * Convert @p value into a string and store it in @p buffer
    UART_send_string(&buffer[0]); /// * Send @p buffer using #UART_send_string()
}
///**@brief This function convert a number to string and then send it using UART
//* @param value integer to be send
//*/
void display_value_s(int16_t value)
{   
    char buffer[7]; /// * Define @p buffer to used it for store character storage
    itoa(buffer,value,10);  /// * Convert @p value into a string and store it in @p buffer
    UART_send_string(&buffer[0]); /// * Send @p buffer using #UART_send_string()
}
void temp_protection()
{
    if (conv && (tavg > 350)){
        UART_send_string((char*)"HIGH_TEMP:");
        STOP_CONVERTER(); /// -# Stop the converter by calling the #STOP_CONVERTER() macro.
        state = STANDBY; /// -# Go to the #STANDBY state.
    }
}
/**@brief This function activate the desired relay in the switcher board according to the value
* of #cell_count
*/
void Cell_ON()
{
    if (cell_count == '1') /// If cell_count = '1'
    {
        CELL1_ON(); /// * Turn ON cell #1 by calling #CELL1_ON
        __delay_ms(10);
        CELL2_OFF(); /// * Turn OFF cell #2 by calling #CELL2_OFF
        __delay_ms(10);        
        CELL3_OFF(); /// * Turn OFF cell #3 by calling #CELL3_OFF
        __delay_ms(10);
        CELL4_OFF(); /// * Turn OFF cell #4 by calling #CELL4_OFF
        __delay_ms(10);
    }else if (cell_count == '2')
    {
        CELL1_OFF(); /// * Turn OFF cell #1 by calling #CELL1_OFF
        __delay_ms(10);
        CELL2_ON(); /// * Turn ON cell #2 by calling #CELL2_ON
        __delay_ms(10);
        CELL3_OFF(); /// * Turn OFF cell #3 by calling #CELL3_OFF
        __delay_ms(10);
        CELL4_OFF(); /// * Turn OFF cell #4 by calling #CELL4_OFF
        __delay_ms(10);
    }else if (cell_count == '3')
    {
        CELL1_OFF(); /// * Turn OFF cell #1 by calling #CELL1_OFF
        __delay_ms(10);
        CELL2_OFF(); /// * Turn OFF cell #2 by calling #CELL2_OFF
        __delay_ms(10);
        CELL3_ON(); /// * Turn ON cell #3 by calling #CELL3_ON
        __delay_ms(10);
        CELL4_OFF(); /// * Turn OFF cell #4 by calling #CELL4_OFF    
    }else if (cell_count == '4')
    {
        CELL1_OFF(); /// * Turn OFF cell #1 by calling #CELL1_OFF
        __delay_ms(10);
        CELL2_OFF(); /// * Turn OFF cell #2 by calling #CELL2_OFF
        __delay_ms(10);
        CELL3_OFF(); /// * Turn OFF cell #3 by calling #CELL3_OFF
        __delay_ms(10);
        CELL4_ON(); /// * Turn ON cell #4 by calling #CELL4_ON
        __delay_ms(10);
    }
}
/**@brief This function deactivate all relays in the switcher board
*/
void Cell_OFF()
{
    CELL1_OFF(); /// * Turn OFF cell #1 by calling #CELL1_OFF
    __delay_ms(10);
    CELL2_OFF(); /// * Turn OFF cell #2 by calling #CELL2_OFF
    __delay_ms(10);
    CELL3_OFF(); /// * Turn OFF cell #3 by calling #CELL3_OFF
    __delay_ms(10);
    CELL4_OFF(); /// * Turn OFF cell #4 by calling #CELL4_OFF  
    __delay_ms(10);
}