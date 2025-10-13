/*
 * arch_avr_extint.h
 *
 *  Copyright 2021-2025 Clement Savergne <csavergne@yahoo.com>

    This file is part of yasim-avr.

    yasim-avr is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    yasim-avr is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with yasim-avr.  If not, see <http://www.gnu.org/licenses/>.
 */

//=======================================================================================

#ifndef __YASIMAVR_AVR_EXTINT_H__
#define __YASIMAVR_AVR_EXTINT_H__

#include "arch_avr_globals.h"
#include "core/sim_peripheral.h"
#include "core/sim_interrupt.h"
#include "core/sim_pin.h"
#include "core/sim_types.h"

YASIMAVR_BEGIN_NAMESPACE


//=======================================================================================

#define EXTINT_PIN_COUNT        2
#define PCINT_PIN_COUNT         24
#define PCINT_BANK_COUNT        (PCINT_PIN_COUNT / 8)


//=======================================================================================
/**
   \brief Configuration structure for ArchAVR_ExtInt
 */
struct ArchAVR_ExtIntConfig {

    struct ext_int_t {
        int_vect_t vector = AVR_INTERRUPT_NONE;
        pin_id_t pin;
    };

    struct pc_int_t {
        int_vect_t vector = AVR_INTERRUPT_NONE;
        reg_addr_t reg_mask;
        pin_id_t pins[8];
    };

    /// Array of pins for external interrupts
    std::vector<ext_int_t> ext_ints;
    /// Array of pins for Pin Change interrupts
    std::vector<pc_int_t> pc_ints;
    /// Regbit for external interrupt control
    regbit_t rb_extint_ctrl;
    /// Regbit for the external interrupt mask
    regbit_t rb_extint_mask;
    /// Regbit for the external interrupt flags
    regbit_t rb_extint_flag;
    /// Regbit for Pin Change interrupt control
    regbit_t rb_pcint_ctrl;
    /// Regbit for Pin Change interrupt flags
    regbit_t rb_pcint_flag;

};

/**
   \brief Implementation of a model for a External Interrupts peripheral for AVR series
 */
class AVR_ARCHAVR_PUBLIC_API ArchAVR_ExtInt : public Peripheral,
                                             public InterruptHandler {

public:

    enum SignalId {
        Signal_ExtInt,
        Signal_PinChange
    };

    explicit ArchAVR_ExtInt(const ArchAVR_ExtIntConfig& config);

    virtual bool init(Device& device) override;
    virtual void reset() override;
    virtual bool ctlreq(ctlreq_id_t req, ctlreq_data_t* data) override;
    virtual void ioreg_write_handler(reg_addr_t addr, const ioreg_write_t& data) override;
    virtual void interrupt_ack_handler(int_vect_t vector) override;

private:

    const ArchAVR_ExtIntConfig& m_config;
    //Signals that get raised when an external interrupt condition is detected
    Signal m_signal;
    //Backup copies of pin states to detect edges
    uint8_t m_extint_pin_value;
    std::vector<uint8_t> m_pcint_pin_value;
    BoundFunctionSignalHook<ArchAVR_ExtInt> m_pin_hook;

    void pin_signal_raised(const signal_data_t& sigdata, int hooktag);

    uint8_t get_extint_mode(uint8_t pin) const;

};


YASIMAVR_END_NAMESPACE

#endif //__YASIMAVR_AVR_EXTINT_H__
