//
//  CLASS
//

// CLASS -> TRAIT
pub trait Class {
    fn name(&self) -> &'static str;
    fn evaluate(&self, context: &mut crate::runtime::Context) -> crate::Box<dyn crate::runtime::Value>;
}


//
//  CONVERTER
//

// CONVERTER -> STRUCT
pub struct Converter {
    locus: usize,
    memory: crate::Vec<crate::Box <dyn Class>>
}

// CONVERTER -> IMPLEMENTATION
impl Converter {
    pub fn run(&mut self) -> &crate::Vec<crate::Box <dyn Class>> {
        while self.locus < crate::SETTINGS.ir.len() {
            let object = match self.use8() {
                0x01 => self.start(),
                0x02 => self.debug(),
                0x03 => self.declaration(),
                0x04 => self.definition(),
                0x05 => self.node(),
                0x06 => self.equation(),
                0x07 => self.comment(),
                0x08 => self.expression(),
                0x09 => self.term(),
                0x0A => self.factor(),
                0x0B => self.limit(),
                0x0C => self.infinite(),
                0x0D => self.variable(),
                0x0E => self.nest(),
                0x0F => self.vector(),
                0x10 => self.number(),
                _ => crate::stdout::crash(2)
            } as crate::Box<dyn Class>;
            self.memory.push(object);
        };
        return &self.memory;
    }
    fn comment(&mut self) -> crate::Box<dyn Class> {
        crate::stdout::trace("Creating comment data structure");
        return crate::Box::new(crate::Comment::new(
            &self.listchar()
        ));
    }
    fn debug(&mut self) -> crate::Box<dyn Class> {
        crate::stdout::trace("Creating debug data structure");
        return crate::Box::new(crate::Debug::new());
    }
    fn declaration(&mut self) -> crate::Box<dyn Class> {
        crate::stdout::trace("Creating declaration data structure");
        return crate::Box::new(crate::Declaration::new(
            self.use32(),
            self.use32()
        ));
    }
    fn definition(&mut self) -> crate::Box<dyn Class> {
        crate::stdout::trace("Creating definition data structure");
        return crate::Box::new(crate::Definition::new(
            self.use32(),
            self.use32()
        ));
    }
    fn equation(&mut self) -> crate::Box<dyn Class> {
        crate::stdout::trace("Creating equation data structure");
        return crate::Box::new(crate::Equation::new(
            self.use32(), 
            self.use32()
        ));
    }
    fn expression(&mut self) -> crate::Box<dyn Class> {
        crate::stdout::trace("Creating expression data structure");
        return crate::Box::new(crate::Expression::new(
            &self.list32(), 
            &self.list8()
        ));
    }
    fn factor(&mut self) -> crate::Box<dyn Class> {
        crate::stdout::trace("Creating factor data structure");
        return crate::Box::new(crate::Factor::new(
            self.use32(), 
            self.use32()
        ));
    }
    fn infinite(&mut self) -> crate::Box<dyn Class> {
        crate::stdout::trace("Creating infinite data structure");
        return crate::Box::new(crate::Infinite::new());
    }
    fn limit(&mut self) -> crate::Box<dyn Class> {
        crate::stdout::trace("Creating limit data structure");
        return crate::Box::new(crate::Limit::new(
            self.use32(), 
            self.use32(), 
            self.use8(), 
            self.use32(), 
            self.use32()
        ));
    }
    fn nest(&mut self) -> crate::Box<dyn Class> {
        crate::stdout::trace("Creating nest data structure");
        return crate::Box::new(crate::Nest::new(
            self.use32()
        ));
    }
    fn node(&mut self) -> crate::Box<dyn Class> {
        crate::stdout::trace("Creating node data structure");
        return crate::Box::new(crate::Node::new(
            self.use32()
        ));
    }
    fn number(&mut self) -> crate::Box<dyn Class> {
        crate::stdout::trace("Creating number data structure");
        return crate::Box::new(crate::Number::new(
            self.use32(),
            self.use8()
        ));
    }
    fn start(&mut self) -> crate::Box<dyn Class> {
        crate::stdout::trace("Creating start data structure");
        return crate::Box::new(crate::Start::new(
            &self.list32()
        ));
    }
    fn term(&mut self) -> crate::Box<dyn Class> {
        crate::stdout::trace("Creating term data structure");
        return crate::Box::new(crate::Term::new(
            &self.list32(), 
            &self.list32()
        ));
    }
    fn variable(&mut self) -> crate::Box<dyn Class> {
        crate::stdout::trace("Creating variable data structure");
        return crate::Box::new(crate::Variable::new(
            &self.listchar()
        ));
    }
    fn vector(&mut self) -> crate::Box<dyn Class> {
        crate::stdout::trace("Creating vector data structure");
        return crate::Box::new(crate::Vector::new(
            &self.list32()
        ));
    }
}

// CONVERTER -> METHODS
impl Converter {
    pub fn new() -> Self {
        return Converter { 
            locus: 0,
            memory: crate::Vec::<crate::Box <dyn Class>>::new()
        }
    }
    fn use8(&mut self) -> u8 {
        self.check(1);
        let value = crate::SETTINGS.ir[self.locus];
        self.inc(1);
        return value;
    }
    fn use32(&mut self) -> u32 {
        self.check(4);
        let value = &crate::SETTINGS.ir[self.locus..self.locus + 4];
        self.inc(4);
        return u32::from_le_bytes([value[0], value[1], value[2], value[3]]);
    }
    fn list8(&mut self) -> crate::Vec::<u8> {
        let mut values = crate::Vec::<u8>::new();
        loop {match self.use8() {
            0 => break,
            value => values.push(value)
        }}
        return values;
    }
    fn list32(&mut self) -> crate::Vec::<u32> {
        let mut values = crate::Vec::<u32>::new();
        loop {match self.use32() {
            0 => break,
            value => values.push(value)
        }}
        return values;
    }
    fn listchar(&mut self) -> crate::String {
        let mut values = crate::String::new();
        loop {match self.use8() {
            0 => break,
            value => values.push(value as char)
        }}
        return values;
    }
    #[inline(always)]
    fn inc(&mut self, sum: usize) -> () {
        self.locus += sum;
    }
    #[inline(always)]
    fn check(&self, distance: usize) -> () {
        if self.locus + distance > crate::SETTINGS.ir.len() {
            crate::stdout::crash(2);
        }
    }
}